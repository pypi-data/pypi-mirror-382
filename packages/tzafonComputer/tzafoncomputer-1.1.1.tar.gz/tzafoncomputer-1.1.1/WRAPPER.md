# Clean API Wrapper

Simple OOP wrapper for browser automation.

## Usage

```python
from tzafon import Computer

client = Computer()  # Auto-reads COMPUTER_API_KEY env var

with client.create(kind="browser") as computer:
    computer.navigate("https://google.com")
    computer.type("Hello World")
    computer.click(100, 200)
    screenshot = computer.screenshot()
```

## Actions

- `navigate(url)` - Go to URL
- `type(text)` - Type text
- `click(x, y)` - Click at coordinates
- `screenshot()` - Take screenshot
- `double_click(x, y)` - Double-click
- `right_click(x, y)` - Right-click
- `drag(from_x, from_y, to_x, to_y)` - Drag
- `hotkey(*keys)` - Press hotkey combo
- `scroll(direction, amount=None)` - Scroll
- `wait(seconds)` - Wait

## Protected Files

Custom wrapper files in `.stainless-ignore`:
- `src/tzafon/wrapper.py`
- `src/tzafon/async_wrapper.py`
- `src/tzafon/client_extensions.py`

