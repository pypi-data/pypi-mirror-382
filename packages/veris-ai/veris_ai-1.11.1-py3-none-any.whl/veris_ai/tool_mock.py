import inspect
import json
import logging
from collections.abc import Callable
from contextlib import suppress
from contextvars import ContextVar
from functools import wraps
import tenacity
from typing import (
    Any,
    Literal,
    TypeVar,
    get_type_hints,
)


from veris_ai.models import ResponseExpectation, ToolCallOptions
from veris_ai.api_client import get_api_client
from veris_ai.utils import convert_to_type, extract_json_schema, get_function_parameters

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Context variable to store session_id for each call
_session_id_context: ContextVar[str | None] = ContextVar("veris_session_id", default=None)


class VerisSDK:
    """Class for mocking tool calls."""

    def __init__(self) -> None:
        """Initialize the ToolMock class."""
        self._mcp = None

    @property
    def session_id(self) -> str | None:
        """Get the session_id from context variable."""
        return _session_id_context.get()

    def set_session_id(self, session_id: str) -> None:
        """Set the session_id in context variable."""
        _session_id_context.set(session_id)
        logger.info(f"Session ID set to {session_id}")

    def clear_session_id(self) -> None:
        """Clear the session_id from context variable."""
        _session_id_context.set(None)
        logger.info("Session ID cleared")

    @property
    def fastapi_mcp(self) -> Any | None:  # noqa: ANN401
        """Get the FastAPI MCP server."""
        return self._mcp

    def set_fastapi_mcp(self, **params_dict: Any) -> None:  # noqa: ANN401
        """Set the FastAPI MCP server with HTTP transport."""
        from fastapi import Depends, Request  # noqa: PLC0415
        from fastapi.security import OAuth2PasswordBearer  # noqa: PLC0415
        from fastapi_mcp import (  # type: ignore[import-untyped] # noqa: PLC0415
            AuthConfig,
            FastApiMCP,
        )

        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

        async def authenticate_request(
            request: Request,  # noqa: ARG001
            token: str | None = Depends(oauth2_scheme),
        ) -> None:
            if token:
                self.set_session_id(token)

        # Create auth config with dependencies
        auth_config = AuthConfig(
            dependencies=[Depends(authenticate_request)],
        )

        # Merge the provided params with our auth config
        if "auth_config" in params_dict:
            # Merge the provided auth config with our dependencies
            provided_auth_config = params_dict.pop("auth_config")
            if provided_auth_config.dependencies:
                auth_config.dependencies.extend(provided_auth_config.dependencies)
            # Copy other auth config properties if they exist
            for field, value in provided_auth_config.model_dump(exclude_none=True).items():
                if field != "dependencies" and hasattr(auth_config, field):
                    setattr(auth_config, field, value)

        # Create the FastApiMCP instance with merged parameters
        self._mcp = FastApiMCP(
            auth_config=auth_config,
            **params_dict,
        )

    def spy(self) -> Callable:
        """Decorator for spying on tool calls."""

        def decorator(func: Callable) -> Callable:
            """Decorator for spying on tool calls."""
            is_async = inspect.iscoroutinefunction(func)

            @wraps(func)
            async def async_wrapper(*args: tuple[object, ...], **kwargs: Any) -> object:  # noqa: ANN401
                """Async wrapper."""
                session_id = _session_id_context.get()
                if not session_id:
                    return await func(*args, **kwargs)
                parameters = get_function_parameters(func, args, kwargs)
                logger.info(f"Spying on function: {func.__name__}")
                log_tool_call(
                    session_id=session_id,
                    function_name=func.__name__,
                    parameters=parameters,
                    docstring=inspect.getdoc(func) or "",
                )
                result = await func(*args, **kwargs)
                log_tool_response(session_id=session_id, response=result)
                return result

            @wraps(func)
            def sync_wrapper(*args: tuple[object, ...], **kwargs: Any) -> object:  # noqa: ANN401
                """Sync wrapper."""
                session_id = _session_id_context.get()
                if not session_id:
                    return func(*args, **kwargs)
                parameters = get_function_parameters(func, args, kwargs)
                logger.info(f"Spying on function: {func.__name__}")
                log_tool_call(
                    session_id=session_id,
                    function_name=func.__name__,
                    parameters=parameters,
                    docstring=inspect.getdoc(func) or "",
                )
                result = func(*args, **kwargs)
                log_tool_response(session_id=session_id, response=result)
                return result

            return async_wrapper if is_async else sync_wrapper

        return decorator

    def mock(  # noqa: C901, PLR0915
        self,
        mode: Literal["tool", "function"] = "tool",
        expects_response: bool | None = None,
        cache_response: bool | None = None,
    ) -> Callable:
        """Decorator for mocking tool calls."""
        response_expectation = (
            ResponseExpectation.NONE
            if (expects_response is False or (expects_response is None and mode == "function"))
            else ResponseExpectation.REQUIRED
            if expects_response is True
            else ResponseExpectation.AUTO
        )
        cache_response = cache_response or False
        options = ToolCallOptions(
            mode=mode, response_expectation=response_expectation, cache_response=cache_response
        )

        def decorator(func: Callable) -> Callable:  # noqa: C901, PLR0915
            """Decorator for mocking tool calls."""
            is_async = inspect.iscoroutinefunction(func)

            @wraps(func)
            async def async_wrapper(
                *args: tuple[object, ...],
                **kwargs: Any,  # noqa: ANN401
            ) -> object:
                """Async wrapper."""
                session_id = _session_id_context.get()
                if not session_id:
                    logger.info(
                        f"No session ID found, executing original function: {func.__name__}"
                    )
                    return await func(*args, **kwargs)
                parameters = get_function_parameters(func, args, kwargs)
                return mock_tool_call(
                    func,
                    session_id,
                    parameters,
                    options,
                )

            @wraps(func)
            def sync_wrapper(
                *args: tuple[object, ...],
                **kwargs: Any,  # noqa: ANN401
            ) -> object:
                """Sync wrapper."""
                session_id = _session_id_context.get()
                if not session_id:
                    logger.info(
                        f"No session ID found, executing original function: {func.__name__}"
                    )
                    return func(*args, **kwargs)
                parameters = get_function_parameters(func, args, kwargs)
                return mock_tool_call(
                    func,
                    session_id,
                    parameters,
                    options,
                )

            # Return the appropriate wrapper based on whether the function is async
            return async_wrapper if is_async else sync_wrapper

        return decorator

    def stub(self, return_value: Any) -> Callable:  # noqa: ANN401
        """Decorator for stubbing toolw calls."""

        def decorator(func: Callable) -> Callable:
            # Check if the original function is async
            is_async = inspect.iscoroutinefunction(func)

            @wraps(func)
            async def async_wrapper(
                *args: tuple[object, ...],
                **kwargs: Any,  # noqa: ANN401
            ) -> object:
                if not self.session_id:
                    logger.info(
                        f"No session ID found, executing original function: {func.__name__}"
                    )
                    return await func(*args, **kwargs)
                logger.info(f"Stubbing function: {func.__name__}")
                return return_value

            @wraps(func)
            def sync_wrapper(*args: tuple[object, ...], **kwargs: Any) -> object:  # noqa: ANN401
                if not self.session_id:
                    logger.info(
                        f"No session ID found, executing original function: {func.__name__}"
                    )
                    return func(*args, **kwargs)
                logger.info(f"Stubbing function: {func.__name__}")
                return return_value

            # Return the appropriate wrapper based on whether the function is async
            return async_wrapper if is_async else sync_wrapper

        return decorator


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    reraise=True,
)
def mock_tool_call(
    func: Callable,
    session_id: str,
    parameters: dict[str, dict[str, str]],
    options: ToolCallOptions | None = None,
) -> object:
    """Mock tool call."""
    options = options or ToolCallOptions()
    api_client = get_api_client()
    endpoint = api_client.tool_mock_endpoint

    logger.info(f"Simulating function: {func.__name__}")

    type_hints = get_type_hints(func)

    # Extract return type object (not just the name)
    return_type_obj = type_hints.pop("return", Any)
    # Get function docstring
    docstring = inspect.getdoc(func) or ""

    # Clean up parameters for V3 - just send values, not the nested dict
    clean_params: dict[str, Any] = {}
    for key, value in parameters.items():
        if isinstance(value, dict) and "value" in value:
            # Extract just the value from the nested structure
            clean_params[key] = value["value"]
        else:
            # Already clean or unexpected format
            clean_params[key] = value

    # Determine response expectation
    payload = {
        "session_id": session_id,
        "response_expectation": options.response_expectation.value,
        "cache_response": bool(options.cache_response),
        "tool_call": {
            "function_name": func.__name__,
            "parameters": clean_params,
            "return_type": json.dumps(extract_json_schema(return_type_obj)),
            "docstring": docstring,
        },
    }

    mock_result = api_client.post(endpoint, payload)
    logger.info(f"Mock response: {mock_result}")

    if isinstance(mock_result, str):
        with suppress(json.JSONDecodeError):
            mock_result = json.loads(mock_result)
            return convert_to_type(mock_result, return_type_obj)
    return convert_to_type(mock_result, return_type_obj)


def log_tool_call(
    session_id: str,
    function_name: str,
    parameters: dict[str, dict[str, str]],
    docstring: str,
) -> None:
    """Log tool call synchronously to the VERIS logging endpoint."""
    api_client = get_api_client()
    endpoint = api_client.get_log_tool_call_endpoint(session_id)

    # Clean up parameters for V3 - just send values, not the nested dict
    clean_params: dict[str, Any] = {}
    for key, value in parameters.items():
        if isinstance(value, dict) and "value" in value:
            # Extract just the value from the nested structure
            clean_params[key] = value["value"]
        else:
            # Already clean or unexpected format
            clean_params[key] = value

    payload = {
        "function_name": function_name,
        "parameters": clean_params,
        "docstring": docstring,
    }
    try:
        api_client.post(endpoint, payload)
        logger.debug(f"Tool call logged for {function_name}")
    except Exception as e:
        logger.warning(f"Failed to log tool call for {function_name}: {e}")


def log_tool_response(session_id: str, response: Any) -> None:  # noqa: ANN401
    """Log tool response synchronously to the VERIS logging endpoint."""
    api_client = get_api_client()
    endpoint = api_client.get_log_tool_response_endpoint(session_id)

    payload = {
        "response": json.dumps(response, default=str),
    }

    try:
        api_client.post(endpoint, payload)
        logger.debug("Tool response logged")
    except Exception as e:
        logger.warning(f"Failed to log tool response: {e}")


veris = VerisSDK()
