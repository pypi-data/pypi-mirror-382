# Batch Execution API

Perfect for queuing multiple actions and executing them together.

## Usage

```python
from tzafon import asyncComputer

client = asyncComputer()

computer = client.create(kind="browser")
computer.navigate("https://google.com")
computer.type("Hello World")
computer.click(100, 200)

# Execute all queued actions in batch
result = computer.execute()

computer.terminate()
```

## How It Works

1. **Queue Actions** - Each method call queues an action (doesn't execute immediately)
2. **Batch Execute** - `computer.execute()` sends all queued actions to backend
3. **Backend processes** - Actions run sequentially, stops on first error
4. **Results returned** - Get results for all executed actions

## All Actions

```python
computer = client.create(kind="browser")

# Queue actions (chainable)
computer.navigate("https://github.com")
computer.wait(2.0)
computer.scroll("down", amount=500)
computer.hotkey("ctrl", "f")
computer.type("search term")
computer.click(100, 200)
computer.double_click(300, 400)
computer.right_click(500, 600)
computer.drag(100, 100, 200, 200)
computer.screenshot()

# Execute all at once
result = computer.execute()
```

## Response Format

```python
result = computer.execute()

# ComputerExecuteBatchResponse
result.results  # List of ActionResult for each action
result.success  # Overall success status

for i, action_result in enumerate(result.results):
    print(f"Action {i+1}: {action_result.status}")
```

## Context Manager

```python
with client.create(kind="browser") as computer:
    computer.navigate("https://google.com")
    computer.type("Hello World")
    computer.click(100, 200)
    
    result = computer.execute()
    # Automatically terminates on exit
```

## Why Batch Execution?

- **Performance**: Single API call instead of multiple
- **Atomic**: All actions or none (stops on first error)  
- **Simpler**: Queue actions then execute
- **Efficient**: Network optimized

## Comparison

### asyncComputer (Batch)
```python
from tzafon import asyncComputer

client = asyncComputer()
computer = client.create(kind="browser")
computer.navigate("https://google.com")  # Queued
computer.type("Hello")                    # Queued
computer.click(100, 200)                  # Queued
result = computer.execute()               # Execute all
```

### Computer (Immediate)
```python
from tzafon import Computer

client = Computer()
with client.create(kind="browser") as computer:
    computer.navigate("https://google.com")  # Executes immediately
    computer.type("Hello")                    # Executes immediately
    computer.click(100, 200)                  # Executes immediately
```

### AsyncComputer (Async Immediate)
```python
from tzafon import AsyncComputer

client = AsyncComputer()
async with client.create(kind="browser") as computer:
    await computer.navigate("https://google.com")  # Async execute
    await computer.type("Hello")                    # Async execute
    await computer.click(100, 200)                  # Async execute
```

## Choose Your Style

- **`asyncComputer`** - Queue and batch execute
- **`Computer`** - Immediate sync execution
- **`AsyncComputer`** - Immediate async execution

