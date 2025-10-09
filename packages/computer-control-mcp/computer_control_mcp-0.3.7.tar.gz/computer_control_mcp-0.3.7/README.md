# Computer Control MCP

### MCP server that provides computer control capabilities, like mouse, keyboard, OCR, etc. using PyAutoGUI, RapidOCR, ONNXRuntime. Similar to 'computer-use' by Anthropic. With Zero External Dependencies.

<div align="center" style="text-align:center;font-family: monospace; display: flex; align-items: center; justify-content: center; width: 100%; gap: 10px">
    <a href="https://nextjs-boilerplate-ashy-nine-64.vercel.app/demo-computer-control"><img
            src="https://komarev.com/ghpvc/?username=AB498&label=DEMO&style=for-the-badge&color=CC0000" /></a>
    <a href="https://discord.gg/ZeeqSBpjU2"><img
            src="https://img.shields.io/discord/1095854826786668545?style=for-the-badge&color=0000CC" alt="Discord"></a>
    <a href="https://img.shields.io/badge/License-MIT-yellow.svg"><img
            src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&color=00CC00" alt="License: MIT"></a>
    <a href="https://pypi.org/project/computer-control-mcp"><img
            src="https://img.shields.io/pypi/v/computer-control-mcp?style=for-the-badge" alt="PyPi"></a>
</div>

---

![MCP Computer Control Demo](https://github.com/AB498/computer-control-mcp/blob/main/demonstration.gif?raw=true)

## Quick Usage (MCP Setup Using `uvx`)

***Note:** Running `uvx computer-control-mcp@latest` for the first time will download python dependencies (around 70MB) which may take some time. Recommended to run this in a terminal before using it as MCP. Subsequent runs will be instant.* 

```json
{
  "mcpServers": {
    "computer-control-mcp": {
      "command": "uvx",
      "args": ["computer-control-mcp@latest"]
    }
  }
}
```

OR install globally with `pip`:
```bash
pip install computer-control-mcp
```
Then run the server with:
```bash
computer-control-mcp # instead of uvx computer-control-mcp, so you can use the latest version, also you can `uv cache clean` to clear the cache and `uvx` again to use latest version.
```

## Features

- Control mouse movements and clicks
- Type text at the current cursor position
- Take screenshots of the entire screen or specific windows with optional saving to downloads directory
- Extract text from screenshots using OCR (Optical Character Recognition)
- List and activate windows
- Press keyboard keys
- Drag and drop operations

## Available Tools

### Mouse Control
- `click_screen(x: int, y: int)`: Click at specified screen coordinates
- `move_mouse(x: int, y: int)`: Move mouse cursor to specified coordinates
- `drag_mouse(from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5)`: Drag mouse from one position to another
- `mouse_down(button: str = "left")`: Hold down a mouse button ('left', 'right', 'middle')
- `mouse_up(button: str = "left")`: Release a mouse button ('left', 'right', 'middle')

### Keyboard Control
- `type_text(text: str)`: Type the specified text at current cursor position
- `press_key(key: str)`: Press a specified keyboard key
- `key_down(key: str)`: Hold down a specific keyboard key until released
- `key_up(key: str)`: Release a specific keyboard key
- `press_keys(keys: Union[str, List[Union[str, List[str]]]])`: Press keyboard keys (supports single keys, sequences, and combinations)

### Screen and Window Management
- `take_screenshot(title_pattern: str = None, use_regex: bool = False, threshold: int = 60, scale_percent_for_ocr: int = None, save_to_downloads: bool = False)`: Capture screen or window
- `take_screenshot_with_ocr(title_pattern: str = None, use_regex: bool = False, threshold: int = 10, scale_percent_for_ocr: int = None, save_to_downloads: bool = False)`: Extract adn return text with coordinates using OCR from screen or window
- `get_screen_size()`: Get current screen resolution
- `list_windows()`: List all open windows
- `activate_window(title_pattern: str, use_regex: bool = False, threshold: int = 60)`: Bring specified window to foreground
- `wait_milliseconds(milliseconds: int)`: Wait for a specified number of milliseconds

## Development

### Setting up the Development Environment

```bash
# Clone the repository
git clone https://github.com/AB498/computer-control-mcp.git
cd computer-control-mcp

# Install in development mode
pip install -e .

# Start server
python -m computer_control_mcp.core

# -- OR --

# Build after `pip install hatch`
hatch build

# Windows
$latest = Get-ChildItem .\dist\*.whl | Sort-Object LastWriteTime -Descending | Select-Object -First 1
pip install $latest.FullName --upgrade 

# Non-windows
pip install dist/*.whl --upgrade

# Run
computer-control-mcp
```

### Running Tests

```bash
python -m pytest
```

## API Reference

See the [API Reference](docs/api.md) for detailed information about the available functions and classes.

## License

MIT

## For more information or help

- [Email (abcd49800@gmail.com)](mailto:abcd49800@gmail.com)
- [Discord (CodePlayground)](https://discord.gg/ZeeqSBpjU2)
