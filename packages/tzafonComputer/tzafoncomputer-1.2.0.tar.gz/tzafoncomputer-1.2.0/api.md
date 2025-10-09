# Computers

Types:

```python
from tzafonComputer.types import (
    ActionResult,
    ComputerResponse,
    ComputerListResponse,
    ComputerExecuteBatchResponse,
    ComputerKeepAliveResponse,
)
```

Methods:

- <code title="post /computers">client.computers.<a href="./src/tzafonComputer/resources/computers.py">create</a>(\*\*<a href="src/tzafonComputer/types/computer_create_params.py">params</a>) -> <a href="./src/tzafonComputer/types/computer_response.py">ComputerResponse</a></code>
- <code title="get /computers/{id}">client.computers.<a href="./src/tzafonComputer/resources/computers.py">retrieve</a>(id) -> <a href="./src/tzafonComputer/types/computer_response.py">ComputerResponse</a></code>
- <code title="get /computers">client.computers.<a href="./src/tzafonComputer/resources/computers.py">list</a>() -> <a href="./src/tzafonComputer/types/computer_list_response.py">ComputerListResponse</a></code>
- <code title="post /computers/{id}/execute">client.computers.<a href="./src/tzafonComputer/resources/computers.py">execute_action</a>(id, \*\*<a href="src/tzafonComputer/types/computer_execute_action_params.py">params</a>) -> <a href="./src/tzafonComputer/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/batch">client.computers.<a href="./src/tzafonComputer/resources/computers.py">execute_batch</a>(id, \*\*<a href="src/tzafonComputer/types/computer_execute_batch_params.py">params</a>) -> <a href="./src/tzafonComputer/types/computer_execute_batch_response.py">ComputerExecuteBatchResponse</a></code>
- <code title="post /computers/{id}/keepalive">client.computers.<a href="./src/tzafonComputer/resources/computers.py">keep_alive</a>(id) -> <a href="./src/tzafonComputer/types/computer_keep_alive_response.py">ComputerKeepAliveResponse</a></code>
- <code title="post /computers/{id}/navigate">client.computers.<a href="./src/tzafonComputer/resources/computers.py">navigate</a>(id, \*\*<a href="src/tzafonComputer/types/computer_navigate_params.py">params</a>) -> <a href="./src/tzafonComputer/types/action_result.py">ActionResult</a></code>
- <code title="get /computers/{id}/events">client.computers.<a href="./src/tzafonComputer/resources/computers.py">stream_events</a>(id) -> None</code>
- <code title="delete /computers/{id}">client.computers.<a href="./src/tzafonComputer/resources/computers.py">terminate</a>(id) -> None</code>
