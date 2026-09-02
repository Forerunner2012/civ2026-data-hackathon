from __future__ import annotations

import json
import math
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from civ_workshop.artifacts import require_mapping, require_string
from civ_workshop.contracts import require_closed_fields, require_stable_contract
from civ_workshop.errors import CivError
from civ_workshop.models import ResourceBinding

EARTH_MEAN_RADIUS_M = 6_371_008.8


@dataclass(frozen=True, order=True)
class GeographicPoint:
    point_id: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class PointResource:
    binding: ResourceBinding
    sha256: str
    points: tuple[GeographicPoint, ...]

    def provenance(self) -> dict[str, str]:
        return {
            "contract": self.binding.contract,
            "name": self.binding.name,
            "path": self.binding.path,
            "sha256": self.sha256,
        }


def _coordinate(value: object, context: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CivError(f"{context} must be a finite number")
    coordinate = float(value)
    if not math.isfinite(coordinate):
        raise CivError(f"{context} must be a finite number")
    if not minimum <= coordinate <= maximum:
        raise CivError(f"{context} must be between {minimum:g} and {maximum:g}")
    return coordinate


def _read_resource(path: Path, name: str, display_path: str) -> tuple[dict[str, object], str]:
    if not path.is_file():
        raise CivError(f"resource '{name}' does not exist: {display_path}")
    try:
        resource_bytes = path.read_bytes()
        raw = json.loads(
            resource_bytes.decode("utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise CivError(f"cannot read resource '{name}' {display_path}: {error}") from error
    return require_mapping(raw, f"resource '{name}'"), sha256(resource_bytes).hexdigest()


def load_point_resources(
    spec_path: Path, bindings: tuple[ResourceBinding, ...]
) -> dict[str, PointResource]:
    loaded: dict[str, PointResource] = {}
    resource_root = spec_path.parent.resolve()
    for binding in bindings:
        path = (resource_root / Path(binding.path)).resolve()
        try:
            path.relative_to(resource_root)
        except ValueError as error:
            raise CivError(
                f"resources.{binding.name}.path must be a relative POSIX path "
                "inside the EventSpec directory"
            ) from error
        document, resource_hash = _read_resource(path, binding.name, binding.path)
        contract = require_stable_contract(
            document.get("contract"),
            kind="point resource",
            expected="civ.point-resource/v1",
            candidate="civ.point-resource/v1alpha1",
        )
        if contract != binding.contract:
            raise CivError(
                f"resource '{binding.name}' has unsupported contract '{contract}'"
            )
        require_closed_fields(document, kind="point resource", expected="civ.point-resource/v1")
        if document.get("coordinate_reference") != "EPSG:4326":
            raise CivError(
                f"resource '{binding.name}' coordinate_reference must be EPSG:4326"
            )
        raw_points = document.get("points")
        if not isinstance(raw_points, list) or not raw_points:
            raise CivError(
                f"resource '{binding.name}' points must contain at least one point"
            )
        points: list[GeographicPoint] = []
        seen_ids: set[str] = set()
        for index, raw_point in enumerate(raw_points):
            point = require_mapping(raw_point, f"resource '{binding.name}' point {index}")
            point_id = require_string(
                point.get("id"), f"resource '{binding.name}' point {index} id"
            )
            if point_id in seen_ids:
                raise CivError(f"resource '{binding.name}' point id '{point_id}' is duplicated")
            seen_ids.add(point_id)
            points.append(
                GeographicPoint(
                    point_id=point_id,
                    latitude=_coordinate(
                        point.get("latitude"),
                        f"resource '{binding.name}' point '{point_id}' latitude",
                        -90,
                        90,
                    ),
                    longitude=_coordinate(
                        point.get("longitude"),
                        f"resource '{binding.name}' point '{point_id}' longitude",
                        -180,
                        180,
                    ),
                )
            )
        loaded[binding.name] = PointResource(
            binding=binding,
            sha256=resource_hash,
            points=tuple(sorted(points)),
        )
    return loaded


def minimum_distance_m(
    resource: PointResource, latitude: object, longitude: object, derivation_name: str
) -> float:
    source_latitude = _coordinate(
        latitude, f"derive.{derivation_name} latitude", -90, 90
    )
    source_longitude = _coordinate(
        longitude, f"derive.{derivation_name} longitude", -180, 180
    )
    latitude_radians = math.radians(source_latitude)
    longitude_radians = math.radians(source_longitude)
    distances: list[float] = []
    for point in resource.points:
        target_latitude = math.radians(point.latitude)
        target_longitude = math.radians(point.longitude)
        latitude_delta = target_latitude - latitude_radians
        longitude_delta = target_longitude - longitude_radians
        haversine = (
            math.sin(latitude_delta / 2) ** 2
            + math.cos(latitude_radians)
            * math.cos(target_latitude)
            * math.sin(longitude_delta / 2) ** 2
        )
        central_angle = 2 * math.asin(math.sqrt(min(1.0, haversine)))
        distances.append(EARTH_MEAN_RADIUS_M * central_angle)
    return round(min(distances), 6)
