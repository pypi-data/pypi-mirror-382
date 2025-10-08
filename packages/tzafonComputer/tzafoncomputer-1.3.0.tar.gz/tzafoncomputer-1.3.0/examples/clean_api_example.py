"""Clean API examples for Tzafon browser automation."""

from tzafon import Computer, asyncComputer

# 1. IMMEDIATE EXECUTION (Computer)
client = Computer()

# Context manager (auto-cleanup)
with client.create(kind="browser") as computer:
    computer.navigate("https://google.com")
    computer.type("Hello World")
    computer.click(100, 200)
    screenshot = computer.screenshot()
    print(f"Screenshot: {screenshot.result['screenshot_url']}")

# All available actions
with client.create(kind="browser") as computer:
    computer.navigate("https://github.com")
    computer.wait(2.0)
    computer.scroll("down", amount=500)
    computer.hotkey("ctrl", "f")
    computer.type("search term")
    computer.click(100, 200)
    computer.double_click(300, 400)
    computer.right_click(500, 600)
    computer.drag(100, 100, 200, 200)


# 2. BATCH EXECUTION (asyncComputer)
batch_client = asyncComputer()

computer = batch_client.create(kind="browser")
computer.navigate("https://google.com")
computer.type("Hello World")
computer.click(100, 200)

# Execute all queued actions
result = computer.execute()
print(f"Executed {len(result.results)} actions")

computer.terminate()
