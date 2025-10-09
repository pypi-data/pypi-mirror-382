import time
from datetime import datetime
from pathlib import Path

import pyautogui
import typer
import yaml
from pynput import keyboard, mouse
from rich.console import Console

app = typer.Typer(
    help="ReplayKit - Record and replay mouse, keyboard, and scroll actions"
)
console = Console()

# Global variables for recording
recorded_actions = []
start_time = None
recording = False
listener_mouse = None
listener_keyboard = None


class ActionRecorder:
    def __init__(self):
        self.actions = []
        self.start_time = None
        self.recording = False
        self.ctrl_pressed = False

    def start_recording(self):
        self.actions = []
        self.start_time = time.time()
        self.recording = True
        self.ctrl_pressed = False
        console.print(
            "[green]Recording started! Press Ctrl+Esc to stop recording.[/green]"
        )
        console.print("[yellow]Actions being recorded:[/yellow]")
        console.print("  - Mouse movements")
        console.print("  - Mouse clicks (left, right, middle)")
        console.print("  - Scroll events")
        console.print("  - Keyboard events (keydown/keyup for proper combos)")

    def stop_recording(self):
        self.recording = False
        console.print("\n[green]Recording stopped![/green]")

    def add_action(
        self,
        action_type: str,
        x: int = 0,
        y: int = 0,
        button: str = None,
        scroll_dx: int = 0,
        scroll_dy: int = 0,
        key: str = None,
    ):
        if not self.recording:
            return

        elapsed_time = time.time() - self.start_time
        action = {
            "timestamp": elapsed_time,
            "type": action_type,
        }

        # Only add x, y for mouse actions
        if action_type in ["click", "move", "scroll"]:
            action["x"] = x
            action["y"] = y

        if button:
            action["button"] = button
        if scroll_dx or scroll_dy:
            action["scroll_dx"] = scroll_dx
            action["scroll_dy"] = scroll_dy
        if key:
            action["key"] = key

        self.actions.append(action)

        # Print action info
        if action_type == "click":
            console.print(f"  [{elapsed_time:.2f}s] Click {button} at ({x}, {y})")
        elif action_type == "move":
            console.print(f"  [{elapsed_time:.2f}s] Move to ({x}, {y})")
        elif action_type == "scroll":
            console.print(
                f"  [{elapsed_time:.2f}s] Scroll at ({x}, {y})"
                f" dx={scroll_dx} dy={scroll_dy}"
            )
        elif action_type == "keydown":
            console.print(f"  [{elapsed_time:.2f}s] Key down: {key}")
        elif action_type == "keyup":
            console.print(f"  [{elapsed_time:.2f}s] Key up: {key}")


recorder = ActionRecorder()


def on_click(x, y, button, pressed):
    """Handle mouse click events"""
    if pressed:
        button_name = str(button).split(".")[-1]
        recorder.add_action("click", x, y, button=button_name)


def on_move(x, y):
    """Handle mouse move events"""
    # Only record significant movements to avoid too many actions
    if len(recorder.actions) == 0 or recorder.actions[-1]["type"] != "move":
        recorder.add_action("move", x, y)
    else:
        last_action = recorder.actions[-1]
        # Only record if moved more than 50 pixels
        if abs(last_action["x"] - x) > 50 or abs(last_action["y"] - y) > 50:
            recorder.add_action("move", x, y)


def on_scroll(x, y, dx, dy):
    """Handle scroll events"""
    recorder.add_action("scroll", x, y, scroll_dx=dx, scroll_dy=dy)


def on_press(key):
    """Handle keyboard press events"""
    # Track Ctrl key state for stop recording combo
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        recorder.ctrl_pressed = True

    # Check for Ctrl+Esc to stop recording (don't record this combo)
    if key == keyboard.Key.esc and recorder.ctrl_pressed:
        recorder.stop_recording()
        return False  # Stop listener

    # Record keydown event
    try:
        # Try to get the character
        key_name = key.char
    except AttributeError:
        # Special keys
        key_name = str(key).replace("Key.", "")

    recorder.add_action("keydown", key=key_name)


def on_release(key):
    """Handle keyboard release events"""
    # Track Ctrl key state for stop recording combo
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        recorder.ctrl_pressed = False

    # Record keyup event
    try:
        # Try to get the character
        key_name = key.char
    except AttributeError:
        # Special keys
        key_name = str(key).replace("Key.", "")

    recorder.add_action("keyup", key=key_name)


@app.command()
def record(
    name: str = typer.Argument(..., help="Name for this recording"),
    output_dir: Path = typer.Option(
        "recordings", "--output-dir", "-o", help="Directory to save recordings"
    ),
):
    """
    Record mouse movements, clicks, scrolls, and keystrokes.
    Press Ctrl+Esc to stop recording.
    """
    console.print("[bold blue]ReplayKit - Recording Mode[/bold blue]")
    console.print(f"Recording name: [yellow]{name}[/yellow]")
    console.print()

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create output file path
    safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
    safe_name = safe_name.replace(" ", "_")
    output_file = output_dir / f"{safe_name}.yaml"

    recorder.start_recording()

    # Start listeners
    mouse_listener = mouse.Listener(
        on_move=on_move, on_click=on_click, on_scroll=on_scroll
    )
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    mouse_listener.start()
    keyboard_listener.start()

    # Wait for recording to stop
    keyboard_listener.join()
    mouse_listener.stop()

    # Save recording
    recording_data = {
        "name": name,
        "created_at": datetime.now().isoformat(),
        "total_duration": recorder.actions[-1]["timestamp"] if recorder.actions else 0,
        "action_count": len(recorder.actions),
        "actions": recorder.actions,
    }

    with open(output_file, "w") as f:
        yaml.dump(recording_data, f, default_flow_style=False, sort_keys=False)

    console.print(f"\n[green]✓ Recording saved to: {output_file}[/green]")
    console.print(f"[blue]Total actions recorded: {len(recorder.actions)}[/blue]")
    console.print(
        f"[blue]Duration: {recording_data['total_duration']:.2f} seconds[/blue]"
    )


@app.command()
def play(
    input_file: Path = typer.Argument(..., help="Path to the recording file to play"),
    loop: bool = typer.Option(
        False, "--loop", "-l", help="Loop the playback continuously"
    ),
    loops: int = typer.Option(
        1, "--loops", "-n", help="Number of times to loop (0 for infinite)"
    ),
    speed: float = typer.Option(
        1.0,
        "--speed",
        "-s",
        help="Playback speed multiplier (0.5 = slower, 2.0 = faster)",
    ),
    delay: float = typer.Option(
        0.0, "--delay", "-d", help="Delay in seconds between loops"
    ),
):
    """
    Play back a recorded sequence of actions.
    Use --loop or --loops to repeat the playback.
    """
    if not input_file.exists():
        console.print(f"[red]Error: Recording file not found: {input_file}[/red]")
        raise typer.Exit(1)

    # Load recording
    with open(input_file) as f:
        recording_data = yaml.safe_load(f)

    actions = recording_data.get("actions", [])

    if not actions:
        console.print("[red]Error: No actions found in recording[/red]")
        raise typer.Exit(1)

    console.print("[bold blue]ReplayKit - Playback Mode[/bold blue]")
    console.print(
        f"Recording: [yellow]{recording_data.get('name', 'Unknown')}[/yellow]"
    )
    console.print(f"Actions: [blue]{len(actions)}[/blue]")
    console.print(
        f"Duration: [blue]{recording_data.get('total_duration', 0):.2f}s[/blue]"
    )
    console.print(f"Speed: [blue]{speed}x[/blue]")
    console.print()

    # Determine loop count
    if loop:
        loop_count = float("inf")
        console.print("[yellow]Looping infinitely. Press Ctrl+C to stop.[/yellow]")
    else:
        loop_count = loops if loops > 0 else float("inf")
        if loop_count == float("inf"):
            console.print("[yellow]Looping infinitely. Press Ctrl+C to stop.[/yellow]")
        else:
            console.print(f"[yellow]Playing {loop_count} time(s)[/yellow]")

    console.print("[yellow]Starting in 3 seconds...[/yellow]")
    time.sleep(3)

    iteration = 0
    try:
        while iteration < loop_count:
            iteration += 1
            console.print(f"\n[green]Starting playback #{iteration}...[/green]")

            last_timestamp = 0
            for action in actions:
                # Calculate delay based on timestamp
                delay_time = (action["timestamp"] - last_timestamp) / speed
                if delay_time > 0:
                    time.sleep(delay_time)

                # Execute action
                action_type = action["type"]

                if action_type == "move":
                    x, y = action["x"], action["y"]
                    pyautogui.moveTo(x, y, duration=0.1)

                elif action_type == "click":
                    x, y = action["x"], action["y"]
                    button = action.get("button", "left")
                    # Map button names
                    button_map = {
                        "left": "left",
                        "right": "right",
                        "middle": "middle",
                        "Button.left": "left",
                        "Button.right": "right",
                        "Button.middle": "middle",
                    }
                    pyautogui.click(x, y, button=button_map.get(button, "left"))

                elif action_type == "scroll":
                    x, y = action["x"], action["y"]
                    scroll_dy = action.get("scroll_dy", 0)
                    # PyAutoGUI uses positive for up, negative for down
                    pyautogui.scroll(int(scroll_dy * 100))

                elif action_type == "keydown":
                    key = action.get("key")
                    if key:
                        # Map special keys for pyautogui
                        key_map = {
                            "ctrl_l": "ctrl",
                            "ctrl_r": "ctrl",
                            "shift_l": "shift",
                            "shift_r": "shift",
                            "alt_l": "alt",
                            "alt_r": "alt",
                            "alt_gr": "altright",
                            "space": "space",
                            "enter": "enter",
                            "tab": "tab",
                            "backspace": "backspace",
                            "delete": "delete",
                            "home": "home",
                            "end": "end",
                            "page_up": "pageup",
                            "page_down": "pagedown",
                            "up": "up",
                            "down": "down",
                            "left": "left",
                            "right": "right",
                            "esc": "esc",
                            "caps_lock": "capslock",
                            "num_lock": "numlock",
                            "scroll_lock": "scrolllock",
                            "insert": "insert",
                            "pause": "pause",
                            "print_screen": "printscreen",
                            "cmd": "command",
                            "cmd_l": "command",
                            "cmd_r": "command",
                        }

                        mapped_key = key_map.get(key, key)
                        pyautogui.keyDown(mapped_key)

                elif action_type == "keyup":
                    key = action.get("key")
                    if key:
                        # Map special keys for pyautogui
                        key_map = {
                            "ctrl_l": "ctrl",
                            "ctrl_r": "ctrl",
                            "shift_l": "shift",
                            "shift_r": "shift",
                            "alt_l": "alt",
                            "alt_r": "alt",
                            "alt_gr": "altright",
                            "space": "space",
                            "enter": "enter",
                            "tab": "tab",
                            "backspace": "backspace",
                            "delete": "delete",
                            "home": "home",
                            "end": "end",
                            "page_up": "pageup",
                            "page_down": "pagedown",
                            "up": "up",
                            "down": "down",
                            "left": "left",
                            "right": "right",
                            "esc": "esc",
                            "caps_lock": "capslock",
                            "num_lock": "numlock",
                            "scroll_lock": "scrolllock",
                            "insert": "insert",
                            "pause": "pause",
                            "print_screen": "printscreen",
                            "cmd": "command",
                            "cmd_l": "command",
                            "cmd_r": "command",
                        }

                        mapped_key = key_map.get(key, key)
                        pyautogui.keyUp(mapped_key)

                last_timestamp = action["timestamp"]

            console.print(f"[green]✓ Playback #{iteration} completed[/green]")

            # Delay between loops
            if iteration < loop_count and delay > 0:
                console.print(f"[yellow]Waiting {delay}s before next loop...[/yellow]")
                time.sleep(delay)

    except KeyboardInterrupt:
        console.print("\n[yellow]Playback stopped by user[/yellow]")

    console.print("\n[green]Done![/green]")


@app.command()
def list_recordings(
    directory: Path = typer.Option(
        "recordings", "--directory", "-d", help="Directory to list recordings from"
    ),
):
    """
    List all available recordings.
    """
    if not directory.exists():
        console.print(f"[red]Directory not found: {directory}[/red]")
        raise typer.Exit(1)

    console.print("[bold blue]Available Recordings[/bold blue]")
    console.print()

    recordings = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))

    if not recordings:
        console.print("[yellow]No recordings found.[/yellow]")
        return

    for recording_file in sorted(recordings):
        try:
            with open(recording_file) as f:
                data = yaml.safe_load(f)

            console.print(f"[green]* {recording_file.name}[/green]")
            console.print(f"   Name: {data.get('name', 'Unknown')}")
            console.print(f"   Actions: {data.get('action_count', 0)}")
            console.print(f"   Duration: {data.get('total_duration', 0):.2f}s")
            console.print(f"   Created: {data.get('created_at', 'Unknown')}")
            console.print()
        except Exception as e:
            console.print(f"[red]Error reading {recording_file.name}: {e}[/red]")


@app.command()
def info(file: Path = typer.Argument(..., help="Path to the recording file")):
    """
    Show detailed information about a recording.
    """
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)

    with open(file) as f:
        data = yaml.safe_load(f)

    console.print("[bold blue]Recording Information[/bold blue]")
    console.print()
    console.print(f"Name: [yellow]{data.get('name', 'Unknown')}[/yellow]")
    console.print(f"Created: [blue]{data.get('created_at', 'Unknown')}[/blue]")
    console.print(f"Duration: [blue]{data.get('total_duration', 0):.2f}s[/blue]")
    console.print(f"Total Actions: [blue]{data.get('action_count', 0)}[/blue]")
    console.print()

    # Count action types
    actions = data.get("actions", [])
    action_types = {}
    for action in actions:
        action_type = action["type"]
        action_types[action_type] = action_types.get(action_type, 0) + 1

    console.print("[bold]Action Breakdown:[/bold]")
    for action_type, count in action_types.items():
        console.print(f"  {action_type}: {count}")


if __name__ == "__main__":
    app()
