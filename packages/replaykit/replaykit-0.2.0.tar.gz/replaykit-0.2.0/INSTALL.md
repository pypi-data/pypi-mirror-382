# Installation Guide for ReplayKit

## Quick Install

### Windows
```bash
pipx install replaykit
```

### macOS
```bash
pipx install "replaykit[macos]"
```

### Linux
```bash
# Install system dependencies first
sudo apt-get install python3-tk python3-dev  # Debian/Ubuntu

# Then install replaykit
pipx install replaykit
```

## What is pipx?

pipx installs Python CLI applications in isolated environments, preventing dependency conflicts.

Install pipx:
- **Windows**: `python -m pip install --user pipx && python -m pipx ensurepath`
- **macOS**: `brew install pipx && pipx ensurepath`
- **Linux**: `python3 -m pip install --user pipx && python3 -m pipx ensurepath`

## Platform-Specific Dependencies

### macOS Extra Dependencies
The `[macos]` extra installs PyObjC for proper macOS integration:
- pyobjc-core
- pyobjc-framework-Quartz

### Linux System Dependencies
Required system packages (install before pip install):
- **Debian/Ubuntu**: `python3-tk python3-dev`
- **Fedora/RHEL**: `python3-tkinter python3-devel`
- **Arch**: `tk`

### Windows
No extra dependencies needed! Works out of the box.

## Permissions

### macOS
Grant Accessibility permissions:
1. Open System Preferences
2. Go to Security & Privacy → Privacy → Accessibility
3. Add your Terminal application to the list

### Linux
May need to run with appropriate permissions or add your user to the input group:
```bash
sudo usermod -a -G input $USER
```
Then log out and log back in.

### Windows
May need to run as administrator for certain applications.

## Verify Installation

```bash
replaykit --help
```

You should see the help message with available commands.

## First Recording

```bash
replaykit record "My First Recording"
```

Press Ctrl+Esc to stop recording. Your recording will be saved as `recordings/My_First_Recording.yaml`.

## Play It Back

```bash
replaykit play recordings/My_First_Recording.yaml
```

## Troubleshooting

### Command not found
Run `pipx ensurepath` and restart your terminal.

### Permission errors on macOS
Make sure you've granted Accessibility permissions (see above).

### Import errors on Linux
Install the system dependencies listed above.

### Encoding errors on Windows
Use a modern terminal like Windows Terminal or ensure your command prompt supports UTF-8.

## Uninstall

```bash
pipx uninstall replaykit
```

