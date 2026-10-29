# Supplied viewers

Viewers are optional for CLI analysis. If a viewer fails, use `civ sample` or the kit fallback material while a coach investigates.

Use the binary supplied for your session and staged in your platform directory. Verify its SHA-256 against `../checksums/SHA256SUMS` before installing or running it.

| Platform folder | PlotJuggler 3.999.3 | Lichtblick 1.28.0 |
| --- | --- | --- |
| `viewer/windows-amd64/` | `PlotJuggler-3.999.3-Windows-x64.exe` | `lichtblick-1.28.0-win.exe` |
| `viewer/linux-amd64/` | `PlotJuggler-3.999.3-x86_64.AppImage` | `lichtblick-1.28.0-linux-x64.tar.gz` |
| `viewer/macos-universal/` | Not published upstream for this release | `lichtblick-1.28.0-mac-universal.dmg` |

The table identifies the pinned viewer assets; it does not qualify their installation on every listed platform. Large executables stay outside the source repository. If a staged file is missing or its checksum differs, do not fetch an arbitrary replacement during the session; use the SSD copy or ask a coach.

Official upstream references:

- PlotJuggler project: <https://github.com/PlotJuggler/PlotJuggler>
- PlotJuggler releases: <https://github.com/PlotJuggler/PlotJuggler/releases>
- Lichtblick project: <https://github.com/lichtblick-suite/lichtblick>
- Lichtblick releases: <https://github.com/lichtblick-suite/lichtblick/releases>

On a connected machine, the official [Lichtblick web app](https://lichtblick-suite.github.io/lichtblick/) supports visual inspection without installation. The core QuickStart does not depend on it.
