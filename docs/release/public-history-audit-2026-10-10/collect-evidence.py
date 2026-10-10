"""One-session read-only evidence collection. Outputs remain organizer-local."""

import base64
import csv
import hashlib
import io
import json
import re
import subprocess
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree

import cv2
import numpy as np
from PIL import Image
from rapidocr import RapidOCR

# Run from the repository root. Extracted text stays in Git-ignored local storage.
ROOT = Path("tmp/public-history-audit-reproduction")
ROOT.mkdir(parents=True, exist_ok=True)
subprocess.run(["git", "check-ignore", "--quiet", str(ROOT / "private-text.json")], check=True)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


patterns = {
    "private_key": rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "github_token": rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b",
    "aws_access_key": rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "credential_assignment": (
        rb"(?i)(?:password|api[_-]?key|secret[_-]?key)\s*[:=]\s*"
        rb"[\x22\x27][^\x22\x27\r\n]{8,}"
    ),
    "local_path": rb"(?:[A-Z]:[\\/]|/(?:home|Users|mnt)/)[^\s\x22\x27<>]+",
    "contact": rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "operational_url": rb"https?://(?:forms\.gle|docs\.google\.com/forms|drive\.google\.com)/",
    "truth_or_review": (
        rb"(?i)\b(?:ground[_ -]?truth|sealed[_ -]?labels?|review[_ -]?progress|"
        rb"participant[_ -]?annotations?)\b"
    ),
    "geographic_marker": rb"(?i)\b(?:latitude|longitude|coordinates|GPS)\b",
    "lfs_pointer": rb"version https://git-lfs.github.com/spec/v1",
    "mcap_bytes": rb"\x89MCAP0\r\n",
}
compiled = {key: re.compile(value) for key, value in patterns.items()}


def markers(data: bytes) -> dict[str, int]:
    return {
        name: len(pattern.findall(data))
        for name, pattern in compiled.items()
        if pattern.search(data)
    }


refs = []
for record in csv.DictReader(Path(__file__).with_name("refs.tsv").open(), delimiter="\t"):
    refs.append((record["ref"], record["commit"]))
commits = set()
commit_refs = defaultdict(set)
reachable = defaultdict(set)
for ref, sha in refs:
    for line in git("rev-list", "--objects", sha).decode().splitlines():
        reachable[line.split(" ", 1)[0]].add(ref)
    ref_commits = git("rev-list", sha).decode().splitlines()
    commits.update(ref_commits)
    for commit in ref_commits:
        commit_refs[commit].add(ref)
paths = defaultdict(set)
path_refs = defaultdict(set)
for sha in sorted(commits):
    for row in git("ls-tree", "-r", "-l", "-z", sha).split(b"\0"):
        if not row:
            continue
        metadata, path = row.split(b"\t", 1)
        _, kind, blob, size = metadata.split()
        if kind != b"blob":
            continue
        blob = blob.decode()
        paths[blob].add(path.decode())
        path_refs[(blob, path.decode())].update(commit_refs[sha])

ocr = None
rows = []
decks = []
images = []
for blob in sorted(paths):
    data = git("cat-file", "blob", blob)
    row = {
        "git_blob": blob,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "paths": sorted(paths[blob]),
        "refs": sorted(reachable[blob]),
        "markers": markers(data),
        "archive_members": 0,
    }
    if any(path.endswith(".b64") for path in paths[blob]):
        try:
            decoded = base64.b64decode(data, validate=False)
            row["decoded_sha256"] = hashlib.sha256(decoded).hexdigest()
            row["decoded_markers"] = markers(decoded)
        except ValueError:
            row["decoded_status"] = "invalid-base64"
    if zipfile.is_zipfile(io.BytesIO(data)):
        archive_rows = []
        private_text = []
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                if member.file_size > 100_000_000:
                    raise RuntimeError("Archive member exceeds bounded inspection limit")
                content = archive.read(member)
                item = {
                    "member": member.filename,
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "markers": markers(content),
                }
                if member.filename.endswith(".xml") or member.filename.endswith(".rels"):
                    xml = ElementTree.fromstring(content)
                    texts = [
                        node.text or "" for node in xml.iter() if node.tag.rsplit("}", 1)[-1] == "t"
                    ]
                    item["text_characters"] = sum(map(len, texts))
                    item["external_relationships"] = sum(
                        node.attrib.get("TargetMode") == "External" for node in xml.iter()
                    )
                    if texts:
                        private_text.append({"member": member.filename, "text": "\n".join(texts)})
                if (
                    member.filename.startswith("ppt/media/")
                    or member.filename == "docProps/thumbnail.jpeg"
                ):
                    try:
                        image = Image.open(io.BytesIO(content)).convert("RGB")
                        if ocr is None:
                            ocr = RapidOCR()
                        array = np.asarray(image)
                        result = ocr(array)
                        texts = list(result.txts) if result.txts is not None else []
                        item["ocr_status"] = "complete"
                        item["ocr_text_count"] = len(texts)
                        item["ocr_markers"] = markers("\n".join(texts).encode())
                        qr_value, qr_points, _ = cv2.QRCodeDetector().detectAndDecode(array)
                        is_thumbnail = member.filename == "docProps/thumbnail.jpeg"
                        images.append(
                            {
                                "git_blob": blob,
                                "member": member.filename,
                                "sha256": item["sha256"],
                                "thumbnail_ocr_complete": is_thumbnail,
                                "thumbnail_text_count": len(texts) if is_thumbnail else 0,
                                "qr_detected": qr_points is not None,
                                "qr_decoded": bool(qr_value),
                            }
                        )
                        private_text.append(
                            {"member": member.filename, "ocr_text": texts, "qr_value": qr_value}
                        )
                    except Exception as error:
                        item["ocr_status"] = "unsupported-or-failed"
                        item["ocr_error_type"] = type(error).__name__
                archive_rows.append(item)
        row["archive_members"] = len(archive_rows)
        row["archive_markers"] = {
            key: sum(item["markers"].get(key, 0) for item in archive_rows)
            for key in patterns
            if any(key in item["markers"] for item in archive_rows)
        }
        (ROOT / f"{blob}-private-text.json").write_text(json.dumps(private_text, indent=2))
        decks.append({"git_blob": blob, "paths": sorted(paths[blob]), "members": archive_rows})
    rows.append(row)
with (ROOT / "objects.tsv").open("w") as stream:
    writer = csv.writer(stream, delimiter="\t")
    writer.writerow(["git_blob", "bytes", "sha256", "paths", "refs", "markers", "archive_members"])
    for row in rows:
        writer.writerow(
            [
                row["git_blob"],
                row["bytes"],
                row["sha256"],
                json.dumps(row["paths"]),
                json.dumps(row["refs"]),
                json.dumps(row["markers"], sort_keys=True),
                row["archive_members"],
            ]
        )
with (ROOT / "path-refs.tsv").open("w") as stream:
    writer = csv.writer(stream, delimiter="\t")
    writer.writerow(["git_blob", "path", "refs"])
    for (blob, path), containing_refs in sorted(path_refs.items()):
        writer.writerow([blob, path, json.dumps(sorted(containing_refs))])
(ROOT / "objects-private-details.json").write_text(json.dumps(rows, indent=2))
(ROOT / "archive-inventory.json").write_text(json.dumps(decks, indent=2))
(ROOT / "image-inspection.json").write_text(json.dumps(images, indent=2))
summary = {
    "refs": len(refs),
    "commits": len(commits),
    "blobs": len(rows),
    "unique_paths": len(set().union(*paths.values())),
    "blob_path_pairs": len(path_refs),
    "blob_bytes": sum(row["bytes"] for row in rows),
    "marker_blob_counts": {key: sum(key in row["markers"] for row in rows) for key in patterns},
    "archives": len(decks),
    "archive_members": sum(len(deck["members"]) for deck in decks),
    "ocr_media": sum(
        "ocr_status" in item
        for deck in decks
        for item in deck["members"]
        if item["member"].startswith("ppt/media/")
    ),
    "ocr_complete": sum(
        item.get("ocr_status") == "complete"
        for deck in decks
        for item in deck["members"]
        if item["member"].startswith("ppt/media/")
    ),
}
(ROOT / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
