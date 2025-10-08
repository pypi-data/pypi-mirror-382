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

from .base import BaseRouter


class LocalRouter(BaseRouter):
    """
    Execute workflows using a resolver provided by a local
    package which implements the workflows.

    Parameters
    ----------
    resolver : BaseResolver
        A resolver object for the registry which contains all
        required workflows.
    """

    def __init__(self, resolver: "BaseResolver"):
        self._resolver = resolver

    def __call__(self, workflow, data=None):
        """
        Executes the workflow locally.

        Parameters
        ----------
        workflow : str
            Name of the workflow to be executed.
        data : Dict[str, Any], optional
            Any data required by the workflow for execution.
        """
        data = data or {}
        task = self._resolver.get_workflow_task_from_signature(workflow, **data)
        func = self._resolver(task)
        result = func()
        return result
