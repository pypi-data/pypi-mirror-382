# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
)
from warnings import warn

from qctrlcommons.exceptions import QctrlArgumentsValueError

from qctrlworkflowclient.router.api import ApiRouter


def core_workflow(
    get_config: Callable,
    workflow: str,
    formatter: Optional[Callable] = None,
    registry_selector: Optional[Callable] = None,
):
    """
    Decorator for a function which will execute a workflow.
    The decorated function should return the data to be used
    during workflow execution. When being used in a client
    package, it is recommended to use a partial to provide
    a default value for `get_config` e.g.

    fire_opal_workflow = partial(
        core_workflow,
        get_fire_opal_config
    )

    @fire_opal_workflow("execute")
    def execute(...):

    Parameters
    ----------
    get_config : Callable
        Returns a `CoreClientSettings` instance. The configured
        router will be used to execute the workflow.
    workflow : str
        The registered name of the workflow to be executed.
    formatter : Callable, optional
        Optional callable which can be used to format the workflow
        result. The callable should accept exactly one argument
        which is the raw result fo the workflow. If used, the
        decorated function will return the result of this callable.
    registry_selector : Callable, optional
        Optional callable which can be used to select the registry
        to be used for the workflow. The callable should accept
        exactly one argument which is the data returned by the
        decorated function. If used, the decorated function will
        return the result of this callable.
    """

    def decorator(func: Callable):
        @wraps(func)
        def customized_decorator(*args, **kwargs):
            # router is instantiated before function is called
            # so any alteration to settings is visible within
            # the function
            config = get_config()
            router = config.get_router()

            if isinstance(router, ApiRouter):
                router.set_async_state(kwargs.pop("is_async", False))

            data = func(*args, **kwargs)

            # dynamically select the registry to be used if selector provided
            # otherwise the default registry set in the router will be used
            registry = registry_selector(data) if registry_selector else None

            # if the router is an instance of the ApiRouter, pass the registry
            if isinstance(router, ApiRouter):
                result = router(workflow, data, registry=registry)
            else:
                result = router(workflow, data)

            if formatter:
                result = formatter(result)

            return result

        return customized_decorator

    return decorator


def async_core_workflow(
    get_config: Callable,
    workflow: str,
    formatter: Optional[Callable] = None,
    registry_selector: Optional[Callable] = None,
):
    """
    Decorator for a function which will execute asynchronously workflow.
    The decorated function should return the data to be used
    during async workflow execution. When being used in a client
    package, it is recommended to use a partial to provide
    a default value for `get_config` e.g.

    async_fire_opal_workflow = partial(
        async_core_workflow,
        get_fire_opal_config
    )

    @async_fire_opal_workflow("execute")
    def execute(...):

    Parameters
    ----------
    get_config : Callable
        Returns a `CoreClientSettings` instance. The configured
        router will be used to execute the workflow.
    workflow : str
        The registered name of the workflow to be executed.
    formatter : Callable, optional
        Optional callable which can be used to format the workflow
        result. The callable should accept exactly one argument
        which is the raw result fo the workflow. If used, the
        decorated function will return the result of this callable.
    registry_selector : Callable, optional
        Optional callable which can be used to select the registry
        to be used for the workflow. The callable should accept
        exactly one argument which is the data returned by the
        decorated function. If used, the decorated function will
        return the result of this callable.
    """

    def decorator(func: Callable):
        @wraps(func)
        def customized_decorator(*args, **kwargs):
            # router is instantiated before function is called
            # so any alteration to settings is visible within
            # the function
            config = get_config()
            router = config.get_router()

            # Set the async state to True
            router.set_async_state(True)
            if "is_async" in kwargs:
                raise QctrlArgumentsValueError(
                    description="The asynchronous state of this function cannot be altered.",
                    arguments={"is_async": kwargs.get("is_async")},
                )

            data = func(*args, **kwargs)

            # dynamically select the registry to be used if selector provided
            # otherwise the default registry set in the router will be used
            registry = registry_selector(data) if registry_selector else None

            # if the router is an instance of the ApiRouter, pass the registry
            if isinstance(router, ApiRouter):
                result = router(workflow, data, registry=registry)
            else:
                result = router(workflow, data)

            if formatter:
                result = formatter(result)

            return result

        return customized_decorator

    return decorator


def print_warnings(result: Dict[str, Any]):
    """
    Result formatter which prints all `warnings` in
    the result and removes them from the result.
    """
    warnings = result.pop("warnings", [])

    for warning in warnings:
        warn(warning, RuntimeWarning)

    return result
