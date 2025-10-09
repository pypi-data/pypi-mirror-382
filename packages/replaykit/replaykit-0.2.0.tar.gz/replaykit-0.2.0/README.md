# ReplayKit

[![CI/CD](https://github.com/zkhan93/replaykit/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/zkhan93/replaykit/actions/workflows/ci-cd.yml)
[![PyPI version](https://badge.fury.io/py/replaykit.svg)](https://badge.fury.io/py/replaykit)
[![Python Version](https://img.shields.io/pypi/pyversions/replaykit.svg)](https://pypi.org/project/replaykit/)

A powerful Python automation tool to record and replay mouse movements, clicks, scrolls, and keyboard actions. Perfect for automating repetitive tasks, testing workflows, and creating macros!

## ✨ Features

- 🎥 **Record** mouse movements, clicks, scrolls, and keyboard inputs
- ⌨️ **Keyboard Support** - Captures keydown/keyup for proper key combinations (Alt+Tab, Ctrl+C, etc.)
- ▶️ **Playback** recorded actions with customizable speed
- 🔄 **Loop** playback for continuous automation
- 💾 **YAML Format** - Easy-to-read and editable recordings
- 🎨 **Beautiful CLI** interface with Rich
- 📊 View recording details and statistics
- 🔧 **Cross-platform** - Works on Windows, macOS, and Linux

## 📦 Installation

### Windows

#### Using pipx (Recommended)
```bash
# Install pipx if you haven't already
python -m pip install --user pipx
python -m pipx ensurepath

# Install replaykit
pipx install replaykit
```

#### Using pip
```bash
pip install replaykit
```

#### Using uv (Fast!)
```bash
# Install uv if you haven't already
pip install uv

# Install replaykit
uv tool install replaykit
```

### macOS

#### Using pipx (Recommended)
```bash
# Install pipx if you haven't already
brew install pipx
pipx ensurepath

# Install replaykit with macOS dependencies
pipx install "replaykit[macos]"
```

#### Using pip
```bash
pip install "replaykit[macos]"
```

#### Using uv (Fast!)
```bash
# Install uv if you haven't already
brew install uv

# Install replaykit with macOS dependencies
uv tool install "replaykit[macos]"
```

**Note for macOS:** You may need to grant Accessibility permissions:
- Go to System Preferences → Security & Privacy → Privacy → Accessibility
- Add Terminal (or your terminal app) to the list of allowed applications

### Linux

#### Using pipx (Recommended)
```bash
# Install system dependencies first
sudo apt-get install python3-tk python3-dev  # Debian/Ubuntu
# OR
sudo dnf install python3-tkinter python3-devel  # Fedora
# OR
sudo pacman -S tk  # Arch

# Install pipx if you haven't already
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install replaykit
pipx install replaykit
```

#### Using pip
```bash
# Install system dependencies first (see above)

# Install replaykit
pip install replaykit
```

#### Using uv (Fast!)
```bash
# Install system dependencies first (see above)

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install replaykit
uv tool install replaykit
```

**Note for Linux:** You may need to run with appropriate permissions for input control.

### Development Installation

```bash
# Clone the repository
git clone https://github.com/zkhan93/replaykit.git
cd replaykit

# Install with uv (recommended)
uv sync

# Or install with pip in editable mode
pip install -e .

# On macOS, use:
pip install -e ".[macos]"
```

## 🚀 Usage

### Record Actions

Start recording with a name (required):

```bash
replaykit record "My Automation"
```

With custom output directory:

```bash
replaykit record "Login Flow" --output-dir custom_recordings/
```

**During recording:**
- Move your mouse, click, scroll, and type as needed
- All actions including keyboard combinations (Alt+Tab, Ctrl+C, etc.) are captured
- Press **Ctrl+Esc** to stop recording
- Recording will be saved automatically as `My_Automation.yaml`

### Play Back Actions

Play a recorded sequence:

```bash
replaykit play recordings/My_Automation.yaml
```

**Advanced playback options:**

```bash
# Loop 5 times
replaykit play recordings/My_Automation.yaml --loops 5

# Loop infinitely
replaykit play recordings/My_Automation.yaml --loops 0

# Play at 2x speed
replaykit play recordings/My_Automation.yaml --speed 2.0

# Play at 0.5x speed (slower, more reliable)
replaykit play recordings/My_Automation.yaml --speed 0.5

# Add 5 second delay between loops
replaykit play recordings/My_Automation.yaml --loops 3 --delay 5
```

### List Recordings

View all available recordings:

```bash
replaykit list-recordings
```

List from a custom directory:

```bash
replaykit list-recordings --directory custom_recordings/
```

### View Recording Details

Get detailed information about a recording:

```bash
replaykit info recordings/My_Automation.yaml
```

## 📝 Recording Format

Recordings are saved as YAML files with the following structure:

```yaml
name: My Recording
created_at: '2025-10-08T10:30:00'
total_duration: 15.5
action_count: 25
actions:
  - timestamp: 0.5
    type: move
    x: 100
    y: 200
  - timestamp: 1.2
    type: click
    x: 100
    y: 200
    button: left
  - timestamp: 2.0
    type: keydown
    key: alt_l
  - timestamp: 2.1
    type: keydown
    key: tab
  - timestamp: 2.2
    type: keyup
    key: tab
  - timestamp: 2.3
    type: keyup
    key: alt_l
```

**Action Types:**
- `move` - Mouse movement (with x, y coordinates)
- `click` - Mouse click (with x, y, button)
- `scroll` - Scroll event (with x, y, scroll_dx, scroll_dy)
- `keydown` - Key press down (with key name)
- `keyup` - Key release (with key name)

## 💡 Tips

1. **Before recording:** Plan your actions and practice the flow
2. **During recording:** Move deliberately for better results
3. **Keyboard combos:** The keydown/keyup system properly captures combinations like Ctrl+C, Alt+Tab
4. **For loops:** Use `--delay` to give time between iterations
5. **Speed control:** Use `--speed 0.5` for slower, more reliable playback on slow systems
6. **Stop playback:** Press `Ctrl+C` to interrupt infinite loops
7. **Edit recordings:** YAML format makes it easy to manually adjust timing, coordinates, or actions

## 🎯 Use Cases

- **Automation:** Form filling, data entry, repetitive tasks
- **Testing:** UI workflow testing, regression testing
- **Batch Processing:** Bulk downloads, file processing
- **Training:** Create tutorials by recording actions
- **Gaming:** Macro creation for repetitive game actions
- **Accessibility:** Help automate tasks for users with limited mobility

## ⚙️ Platform-Specific Notes

### Windows
- Works out of the box
- May need to run as administrator for certain applications

### macOS
- Requires Accessibility permissions (see installation notes)
- Uses PyObjC for native macOS support
- May need to approve Terminal in System Preferences

### Linux
- Requires X11 (works on most desktop environments)
- May need appropriate permissions for input control
- On Wayland, you may need to run under XWayland

## ⚠️ Safety Notes

**Important:**
- Always review recordings before running them in a loop
- Be careful with click positions on different screen resolutions
- Have a way to quickly stop playback (Ctrl+C)
- Test with `--loops 1` before running infinite loops
- Don't record sensitive information (passwords, personal data)
- Recordings contain exact coordinates - may not work across different displays

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - Feel free to use and modify as needed!

## 🐛 Troubleshooting

### "Permission denied" or accessibility errors
- **macOS:** Grant Accessibility permissions in System Preferences
- **Linux:** Run with appropriate permissions or add your user to input group
- **Windows:** Run as administrator for certain applications

### Recordings don't work on different screen resolutions
- Recordings use absolute coordinates
- Consider using scaling factors or re-record on the target display

### Keyboard combinations not working
- Make sure you're using a recent version with keydown/keyup support
- Check that your recording has both keydown and keyup events for modifier keys

### PyAutoGUI fail-safe triggered
- Moving mouse to corner triggers fail-safe
- You can disable with `pyautogui.FAILSAFE = False` (not recommended)

## 🔗 Links

- Documentation: [GitHub Wiki](https://github.com/zkhan93/replaykit/wiki)
- Issues: [GitHub Issues](https://github.com/zkhan93/replaykit/issues)
- PyPI: [replaykit on PyPI](https://pypi.org/project/replaykit/)
