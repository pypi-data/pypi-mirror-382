# Auth

Types:

```python
from tzafonComputer.types import (
    AuthHandleCallbackResponse,
    AuthLogoutResponse,
    AuthRetrieveCurrentUserResponse,
)
```

Methods:

- <code title="get /auth/callback">client.auth.<a href="./src/tzafonComputer/resources/auth.py">handle_callback</a>(\*\*<a href="src/tzafonComputer/types/auth_handle_callback_params.py">params</a>) -> <a href="./src/tzafonComputer/types/auth_handle_callback_response.py">AuthHandleCallbackResponse</a></code>
- <code title="get /auth/login">client.auth.<a href="./src/tzafonComputer/resources/auth.py">initiate_login</a>() -> None</code>
- <code title="post /auth/logout">client.auth.<a href="./src/tzafonComputer/resources/auth.py">logout</a>() -> <a href="./src/tzafonComputer/types/auth_logout_response.py">AuthLogoutResponse</a></code>
- <code title="get /auth/me">client.auth.<a href="./src/tzafonComputer/resources/auth.py">retrieve_current_user</a>() -> <a href="./src/tzafonComputer/types/auth_retrieve_current_user_response.py">AuthRetrieveCurrentUserResponse</a></code>

# Computers

Types:

```python
from tzafonComputer.types import (
    ActionResult,
    ComputerResponse,
    ComputerExecuteBatchResponse,
    ComputerKeepAliveResponse,
)
```

Methods:

- <code title="post /computers">client.computers.<a href="./src/tzafonComputer/resources/computers.py">create</a>(\*\*<a href="src/tzafonComputer/types/computer_create_params.py">params</a>) -> <a href="./src/tzafonComputer/types/computer_response.py">ComputerResponse</a></code>
- <code title="get /computers/{id}">client.computers.<a href="./src/tzafonComputer/resources/computers.py">retrieve</a>(id) -> <a href="./src/tzafonComputer/types/computer_response.py">ComputerResponse</a></code>
- <code title="post /computers/{id}/click">client.computers.<a href="./src/tzafonComputer/resources/computers.py">click</a>(id, \*\*<a href="src/tzafonComputer/types/computer_click_params.py">params</a>) -> <a href="./src/tzafonComputer/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/execute">client.computers.<a href="./src/tzafonComputer/resources/computers.py">execute_action</a>(id, \*\*<a href="src/tzafonComputer/types/computer_execute_action_params.py">params</a>) -> <a href="./src/tzafonComputer/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/batch">client.computers.<a href="./src/tzafonComputer/resources/computers.py">execute_batch</a>(id, \*\*<a href="src/tzafonComputer/types/computer_execute_batch_params.py">params</a>) -> <a href="./src/tzafonComputer/types/computer_execute_batch_response.py">ComputerExecuteBatchResponse</a></code>
- <code title="post /computers/{id}/keepalive">client.computers.<a href="./src/tzafonComputer/resources/computers.py">keep_alive</a>(id) -> <a href="./src/tzafonComputer/types/computer_keep_alive_response.py">ComputerKeepAliveResponse</a></code>
- <code title="post /computers/{id}/navigate">client.computers.<a href="./src/tzafonComputer/resources/computers.py">navigate</a>(id, \*\*<a href="src/tzafonComputer/types/computer_navigate_params.py">params</a>) -> <a href="./src/tzafonComputer/types/action_result.py">ActionResult</a></code>
- <code title="get /computers/{id}/events">client.computers.<a href="./src/tzafonComputer/resources/computers.py">stream_events</a>(id) -> None</code>
- <code title="post /computers/{id}/screenshot">client.computers.<a href="./src/tzafonComputer/resources/computers.py">take_screenshot</a>(id) -> <a href="./src/tzafonComputer/types/action_result.py">ActionResult</a></code>
- <code title="delete /computers/{id}">client.computers.<a href="./src/tzafonComputer/resources/computers.py">terminate</a>(id) -> None</code>
- <code title="post /computers/{id}/type">client.computers.<a href="./src/tzafonComputer/resources/computers.py">type_text</a>(id, \*\*<a href="src/tzafonComputer/types/computer_type_text_params.py">params</a>) -> <a href="./src/tzafonComputer/types/action_result.py">ActionResult</a></code>
