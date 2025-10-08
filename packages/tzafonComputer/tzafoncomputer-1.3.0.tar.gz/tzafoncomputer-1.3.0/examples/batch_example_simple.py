"""Simple batch execution example."""

from tzafon import asyncComputer

client = asyncComputer()

computer = client.create(kind="browser")
computer.navigate("https://google.com")
computer.type("Hello World")
computer.click(100, 200)

# Execute all actions in batch
result = computer.execute()
print(f"✓ Executed {len(result.results)} actions")

computer.terminate()

