# Tzafon Python SDK - Wrapper Functionality

## Overview

Custom OOP wrapper that provides a clean, Pythonic API for browser automation on top of the Stainless-generated SDK.

## What It Does

### Before (Raw SDK)
```python
from tzafon import Computer

client = Computer(api_key="wpk_...")
response = client.computers.create(kind="browser")

# Every action requires this verbose syntax:
client.computers.execute_action(response.id, body={
    "action": {"type": "go_to_url", "url": "https://google.com"}
})
client.computers.execute_action(response.id, body={
    "action": {"type": "type", "text": "Hello"}
})
client.computers.execute_action(response.id, body={
    "action": {"type": "click", "x": 100, "y": 200}
})
client.computers.execute_action(response.id, body={
    "action": {"type": "screenshot"}
})
client.computers.terminate(response.id)
```

### After (Clean Wrapper)
```python
from tzafon import Computer

client = Computer()  # Auto-reads COMPUTER_API_KEY from env

# Context manager handles cleanup automatically
with client.create(kind="browser") as computer:
    computer.navigate("https://google.com")
    computer.type("Hello")
    computer.click(100, 200)
    screenshot = computer.screenshot()
    # Automatically terminates on exit
```

## Architecture

### 3 Custom Files (Protected from Stainless Regeneration)

1. **`src/tzafon/wrapper.py`** - Sync wrapper class
   - `ComputerWrapper` class
   - Clean methods for all 10 action types
   - Context manager support (`__enter__` / `__exit__`)

2. **`src/tzafon/async_wrapper.py`** - Async wrapper class
   - `AsyncComputerWrapper` class
   - Async versions of all methods
   - Async context manager support (`__aenter__` / `__aexit__`)

3. **`src/tzafon/client_extensions.py`** - Client monkey-patching
   - Adds `create()` method to `Computer` class
   - Adds `create()` method to `AsyncComputer` class
   - Returns wrapper instances instead of raw responses

### Integration Point

**`src/tzafon/__init__.py`** (modified once, protected by `.stainless-ignore`)
```python
# Import wrappers
from .wrapper import ComputerWrapper as ComputerWrapper
from .async_wrapper import AsyncComputerWrapper as AsyncComputerWrapper
from .client_extensions import add_client_extensions, add_async_client_extensions

# Apply extensions to Stainless-generated classes
add_client_extensions(Computer)
add_async_client_extensions(AsyncComputer)
```

## Complete API

### Client Setup
```python
from tzafon import Computer

# Reads COMPUTER_API_KEY environment variable
client = Computer()

# Or pass explicitly
client = Computer(api_key="wpk_...")
```

### Creating Computer Instances
```python
# Context manager (recommended - auto cleanup)
with client.create(kind="browser") as computer:
    computer.navigate("https://example.com")

# Manual management
computer = client.create(kind="browser")
try:
    computer.navigate("https://example.com")
finally:
    computer.terminate()
```

### All 10 Actions

#### 1. Navigate
```python
computer.navigate("https://google.com")
# Backend: {"action": {"type": "go_to_url", "url": "..."}}
```

#### 2. Type Text
```python
computer.type("Hello World")
# Backend: {"action": {"type": "type", "text": "..."}}
```

#### 3. Click
```python
computer.click(100, 200)
# Backend: {"action": {"type": "click", "x": 100, "y": 200}}
```

#### 4. Screenshot
```python
result = computer.screenshot()
print(result.result['screenshot_url'])
# Backend: {"action": {"type": "screenshot"}}
```

#### 5. Double Click
```python
computer.double_click(300, 400)
# Backend: {"action": {"type": "double_click", "x": 300, "y": 400}}
```

#### 6. Right Click
```python
computer.right_click(500, 600)
# Backend: {"action": {"type": "right_click", "x": 500, "y": 600}}
```

#### 7. Drag
```python
computer.drag(from_x=100, from_y=100, to_x=200, to_y=200)
# Backend: {"action": {"type": "drag", "from_x": 100, "from_y": 100, "to_x": 200, "to_y": 200}}
```

#### 8. Hotkey
```python
computer.hotkey("ctrl", "f")  # Ctrl+F
computer.hotkey("cmd", "c")   # Cmd+C
# Backend: {"action": {"type": "hotkey", "keys": ["ctrl", "f"]}}
```

#### 9. Scroll
```python
computer.scroll("down")
computer.scroll("down", amount=500)
# Backend: {"action": {"type": "scroll", "direction": "down", "amount": 500}}
```

#### 10. Wait
```python
computer.wait(2.0)  # Wait 2 seconds
# Backend: {"action": {"type": "wait", "seconds": 2.0}}
```

### Response Format

All actions return `ActionResult`:
```python
ActionResult(
    status='SUCCESS',           # 'SUCCESS' or 'ERROR'
    error_message=None,         # Error details if failed
    result={'screenshot_url': '...'},  # Action-specific data
    timestamp='2025-10-07T18:14:47Z'
)
```

## Async Support

```python
from tzafon import AsyncComputer

async def main():
    client = AsyncComputer()
    
    async with client.create(kind="browser") as computer:
        await computer.navigate("https://google.com")
        await computer.type("Hello")
        await computer.click(100, 200)
        screenshot = await computer.screenshot()

import asyncio
asyncio.run(main())
```

## Benefits

1. **Clean API**: `computer.navigate(url)` vs `client.computers.execute_action(id, body={...})`
2. **Auto-cleanup**: Context managers handle termination automatically
3. **Type safety**: Proper method signatures with IDE autocomplete
4. **Both sync and async**: Full async support with `AsyncComputer`
5. **Protected from regeneration**: `.stainless-ignore` prevents Stainless overwrites
6. **Backward compatible**: Original SDK methods still work

## Original SDK Still Available

```python
# You can still use the raw SDK if needed
client = Computer()
response = client.computers.create(kind="browser")
client.computers.execute_action(response.id, body={"action": {...}})
client.computers.terminate(response.id)
```

## Files Summary

**Custom Files (Protected):**
- `src/tzafon/wrapper.py` - Sync wrapper
- `src/tzafon/async_wrapper.py` - Async wrapper  
- `src/tzafon/client_extensions.py` - Monkey-patching
- `.stainless-ignore` - Protection config

**Modified Once:**
- `src/tzafon/__init__.py` - Imports and applies extensions

**Examples:**
- `examples/clean_api_example.py` - Usage examples
- `WRAPPER.md` - Quick reference

## Environment Setup

```bash
export COMPUTER_API_KEY=wpk_QUCIth7oNvAei4hV2i1c9uDl5yLaVmRJ
```

## Testing

```python
from tzafon import Computer

client = Computer()

with client.create(kind="browser") as computer:
    computer.navigate("https://google.com")
    computer.type("Hello World")
    result = computer.screenshot()
    print(f"Status: {result.status}")
    print(f"Screenshot: {result.result['screenshot_url']}")
```

**Actual Output:**
```
ActionResult(
    error_message=None, 
    result={'screenshot_url': 'https://...'}, 
    status='SUCCESS', 
    timestamp='2025-10-07T18:15:03Z'
)
```

