"""Batch execution example - queue actions and execute together."""

from tzafon import asyncComputer

# Create client
client = asyncComputer()

# Create computer and queue actions
computer = client.create(kind="browser")
computer.navigate("https://google.com")
computer.type("Hello World")
computer.click(100, 200)

# Execute all actions in batch
result = computer.execute()
print(f"Executed {len(result.results)} actions")
for i, action_result in enumerate(result.results):
    print(f"  Action {i+1}: {action_result.status}")

# Clean up
computer.terminate()


# Using context manager
with client.create(kind="browser") as computer:
    computer.navigate("https://github.com")
    computer.wait(2.0)
    computer.scroll("down", amount=500)
    computer.hotkey("ctrl", "f")
    computer.type("search term")
    computer.click(300, 400)
    
    # Execute all queued actions
    result = computer.execute()
    print(f"Batch execution: {len(result.results)} actions completed")

