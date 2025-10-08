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
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
)
from warnings import warn

import gql
from qctrlclient import GraphQLClient
from qctrlclient.exceptions import GraphQLClientError
from qctrlcommons.preconditions import check_argument
from qctrlcommons.serializers import (
    DataTypeDecoder,
    DataTypeEncoder,
)
from tenacity import (
    retry,
    retry_if_result,
    wait_chain,
    wait_fixed,
)

from qctrlworkflowclient.products import Product
from qctrlworkflowclient.settings import CoreClientSettings
from qctrlworkflowclient.utils import get_installed_version

from .base import BaseRouter

# every 2s for the first 30s, then every 10s
_POLL_WAIT_CHAIN = wait_chain(*[wait_fixed(2) for _ in range(15)] + [wait_fixed(10)])

# Max payload size that can be sent to server is 50 MB.
# See https://architecture.q-ctrl.com/Documentation/Jobs/system-limits/ for reference.
_MAX_PAYLOAD_SIZE_MB = 50


class ActionStatus(Enum):
    """
    Valid Action statuses.
    """

    SUCCESS = "SUCCESS"  # has completed
    FAILURE = "FAILURE"  # has failed
    REVOKED = "REVOKED"  # has been cancelled
    PENDING = "PENDING"  # is queued
    RECEIVED = "RECEIVED"  # has been received
    RETRY = "RETRY"  # is retrying
    STARTED = "STARTED"  # has started


@dataclass
class Organization:
    """
    Simple client-side representation of an Organization.

    Parameters
    ----------
    organization_id : str
        The unique organization identifier.
    slug : str
        The unique organization slug.
    name : str
        The name of the organization.
    """

    organization_id: str
    slug: str
    name: str

    def to_dict(self) -> Dict[str, str]:
        """
        The dictionary representation of the organization.
        """
        return {"id": self.organization_id, "slug": self.slug, "name": self.name}


@dataclass
class DecodedResult:
    """
    Store the result returned from the server.
    This wraps the decoded data with extra information that might be needed in
    the client packages.

    Parameters
    ----------
    decoded: Any
        The decoded result. The None case should be handled by the client package.
    action_id : str
        The action id for the task.
    """

    decoded: Any
    action_id: str


@dataclass
class Action:
    """
    Simple client-side representation of the Action model.

    Parameters
    ----------
    action_id : str
        The unique action identifier.
    status : str, optional
        The current status of the action.
    raw_result : Any, options
        The raw, encoded result retrieved from the
        API. Use the `result` property to get the
        decoded result.
    errors : List[Dict[str, Any]], optional
        List of any errors that occurred during
        execution.
    """

    action_id: str
    status: Optional[str] = None
    raw_result: Optional[Any] = None
    errors: Optional[List[Dict[str, Any]]] = None

    @property
    def result(self) -> DecodedResult:
        """
        Return the decoded result.
        """
        _result = self.raw_result

        if _result is not None:
            _result = json.loads(_result, cls=DataTypeDecoder)

        return DecodedResult(_result, self.action_id)

    def is_finished(self) -> bool:
        """
        Check if the action has finished.
        """
        return self.status in (
            ActionStatus.SUCCESS.value,
            ActionStatus.FAILURE.value,
            ActionStatus.REVOKED.value,
        )

    def is_failed(self) -> bool:
        """
        Check if the action failed.
        """
        return self.status == ActionStatus.FAILURE.value

    def is_revoked(self) -> bool:
        """
        Check if the action was revoked.
        """
        return self.status == ActionStatus.REVOKED.value


class ApiRouter(BaseRouter):
    """
    Remotely execute the workflow using the `startCoreWorkflow`
    GraphQL mutation.

    Parameters
    ----------
    client : GraphQLClient
        The GraphQL client used to make the request to execute
        the workflow remotely.
    registry : Registry
        The registry that the workflows being executed are
        registered in.
    """

    _TRACKED_PACKAGES = [
        "boulder-opal",
        "fire-opal",
        "qctrl-client",
        "qctrl-commons",
        "qctrl-workflow-client",
    ]

    def __init__(self, client: GraphQLClient, settings: CoreClientSettings):
        self._client = client
        self._settings = settings
        self._validate()
        self._parallel_task_collector = None
        self._async = False

    def set_async_state(self, is_async: bool):
        """
        Toggle asynchronous state of workflow execution.
        """
        self._async = is_async

    def _validate(self):
        """
        Perform validation checks on the settings.
        """

        if not self._settings.product:
            raise GraphQLClientError("`product` must be configured in settings")

        self._check_organization_config()

    def _check_organization_config(self):
        """
        Validate the `organization` configuration. After this
        function finishes, the following will be true:

        - The slug of the organization that the workflow will run
          under will be configured in `settings.organization`.
        - The user is a member of the configured organization.

        If the above rules cannot be guaranteed, an error message
        will be displayed.
        """

        # organization configured by user
        if self._settings.organization:
            found = False

            for organization in self._organizations:
                if organization.slug == self._settings.organization:
                    found = True
                    break

            if not found:
                raise RuntimeError(
                    f"Configured organization not found, is not set up, or does not have valid "
                    f"product access: `{self._settings.organization}`"
                )

        # organization not configured by user
        else:
            # no valid organizations found for the user
            if not self._organizations:
                raise RuntimeError(
                    "No organizations are set up or have a valid subscription to the product. "
                    "Please ensure that your organization is set up and has an active subscription "
                    "to the product you are trying to access. If you believe this is an error, "
                    "contact your Q-CTRL representative or visit the Q-CTRL support portal at "
                    "https://support.q-ctrl.com."
                )

            # user is a member of multiple organizations
            if len(self._organizations) > 1:
                error_message = "You are assigned to multiple organizations. "
                error_message += "Please configure an organization:\n\n"

                for organization in self._organizations:
                    error_message += f"- {organization.slug}\n"

                raise RuntimeError(error_message)

            # user is a member of one organization
            self._settings.organization = self._organizations[0].slug

    @cached_property
    def _organizations(self) -> List[Organization]:
        """
        Return the list of organizations that the user is
        assigned to which provide access to the configured product.
        """

        query = gql.gql(
            """
            query {
                profile {
                    profile {
                        organizations {
                            id
                            slug
                            name
                            products {
                                name
                                active
                            }
                        }
                    }
                    errors {
                        fields
                        message
                    }
                }
            }
        """
        )

        response = self._client.execute(query)
        data = response["profile"]["profile"]["organizations"]
        organizations = []

        for organization_data in data:
            if self._has_product_access(
                organization_data, self._settings.product.value.name
            ):
                organizations.append(
                    Organization(
                        organization_id=organization_data["id"],
                        slug=organization_data["slug"],
                        name=organization_data["name"],
                    )
                )

        return organizations

    @staticmethod
    def _has_product_access(organization_data: Dict, product_name: str) -> bool:
        """
        Convenience function to check if the organization
        has access to the given product. The format of
        `organization_data` is based on the output of the query
        in `_get_organizations`.
        """

        for product_data in organization_data["products"]:
            if product_data["name"] == product_name:
                return product_data["active"]

        return False

    def enable_parallel(
        self, callback: Optional[Callable[[DecodedResult], dict]] = None
    ):
        """
        Return a context manager to collect parallel tasks.

        Parameters
        ----------
        callback : Callable[[DecodedResult], dict] or None, optional
            A callable to run post process on the result returned from the server, if needed.
            Defaults to None, meaning do nothing.
        """
        collector = ParallelCollector(self, callback=callback)
        self._parallel_task_collector = collector
        return collector

    def __call__(self, workflow, data=None, registry=None):
        """
        Executes the workflow through the API.

        Parameters
        ----------
        workflow : str
            Name of the workflow to be executed.
        data : Dict[str, Any], optional
            Any data required by the workflow for execution.
        registry : str, optional
            The registry to be used for the workflow execution.
        """
        query = gql.gql(
            """
            mutation ($input: StartCoreWorkflowInput!) {
                startCoreWorkflow(input: $input) {
                    action {
                        modelId
                        status
                        result
                        errors {
                            exception
                            traceback
                        }
                    }
                    warnings {
                        message
                    }
                    errors {
                        message
                        fields
                    }
                }
            }
        """
        )

        client_metadata = self._get_client_metadata()

        # if registry is not provided, use the default registry
        if registry is None:
            registry = self._settings.product.value.registry
        _data = json.dumps(data, cls=DataTypeEncoder)
        payload_size = len(_data.encode("utf-8"))
        if payload_size > _MAX_PAYLOAD_SIZE_MB * 1e6:
            raise ValueError(
                f"Payload size {payload_size}, exceeds max allowed {_MAX_PAYLOAD_SIZE_MB} MB."
            )
        input_ = {
            "registry": registry,
            "workflow": workflow,
            "data": _data,
            "clientMetadata": json.dumps(client_metadata),
        }

        response = self._client.execute(query, {"input": input_})

        # pylint:disable=unsubscriptable-object

        self._handle_warnings(response["startCoreWorkflow"]["warnings"])
        action_data = response["startCoreWorkflow"]["action"]

        action = Action(
            action_id=action_data["modelId"],
            status=action_data["status"],
            raw_result=action_data["result"],
            errors=action_data["errors"],
        )
        self._settings.event_dispatch("action.updated", action=action)
        if self._async:
            return {"async_result": action}

        if self._parallel_task_collector is not None:
            async_result = {"async_result": action}
            self._parallel_task_collector.add(async_result)
            return async_result

        return self.get_result(action)

    def _get_client_metadata(self) -> Dict[str, Any]:
        """
        Return the client metadata to be included on the
        request to start the workflow.
        """

        package_versions = {}

        for package in self._TRACKED_PACKAGES:
            package_versions[package] = get_installed_version(package)

        return {
            "package_versions": package_versions,
            "organization": self._get_configured_organization().to_dict(),
        }

    def _get_configured_organization(self) -> Organization:
        """
        Return the corresponding `Organization` object for
        the `organization` configured in settings.
        """
        for organization in self._organizations:
            if organization.slug == self._settings.organization:
                return organization

        raise RuntimeError(f"Organization not found: {self._settings.organization}")

    @staticmethod
    def _handle_warnings(warnings_data: List[Dict[str, Any]]):
        """
        Handle warnings returned when starting a workflow.
        """

        for warning_data in warnings_data:
            message = warning_data["message"]
            warn(Warning(message))

    def update_action_status(self, action: Action) -> Action:
        """
        Update the action status. When finished, an updated
        `Action` object is returned.
        """
        _query = gql.gql(
            """
            query($modelId: String!) {
                action(modelId: $modelId) {
                    action {
                        status
                        errors {
                            exception
                            traceback
                        }
                        result
                    }
                    errors {
                        message
                    }
                }
            }
        """
        )

        response = self._client.execute(_query, {"modelId": action.action_id})
        action.status = response["action"]["action"]["status"]
        action.raw_result = response["action"]["action"]["result"]
        action.errors = response["action"]["action"]["errors"]

        self._settings.event_dispatch("action.updated", action=action)

        return action

    @retry(
        wait=_POLL_WAIT_CHAIN,
        retry=retry_if_result(lambda action: not action.is_finished()),
    )
    def _poll_for_completion(self, action: Action) -> Action:
        """
        Poll the API waiting for the action to be finished.
        When finished, an updated `Action` object is returned.
        """
        return self.update_action_status(action)

    def get_result(
        self, action: Action, revoke_on_interrupt: bool = True
    ) -> DecodedResult:
        """
        Return the result of the action.
        """
        return self._fetch_action(action, revoke_on_interrupt).result

    def _fetch_action(self, action: Action, revoke_on_interrupt: bool = True) -> Any:
        """
        Fetch the action from the server. If the action
        has not finished, the API will be polled until it has.
        If the action has failed, a `RuntimeError` will be
        raised.
        """

        if not action.is_finished():
            try:
                action = self._poll_for_completion(action)
            except KeyboardInterrupt as exc:
                if revoke_on_interrupt:
                    if self._settings.product == Product.BOULDER_OPAL:
                        warn(
                            "Keyboard interrupts will not cancel remote jobs in the future. "
                            "To cancel a job, use the BoulderOpalJob.cancel() method instead.",
                            category=FutureWarning,
                            stacklevel=2,
                        )
                    self._revoke_action(action)
                    action = self._poll_for_completion(action)
                else:
                    raise KeyboardInterrupt from exc

        if action.is_failed():
            self._settings.event_dispatch("action.failure", action=action)
            raise RuntimeError(action.errors)

        if action.is_revoked():
            self._settings.event_dispatch("action.revoked", action=action)
            raise RuntimeError(
                f'Your task (action_id="{action.action_id}") has been cancelled.'
            )

        self._settings.event_dispatch("action.success", action=action)
        return action

    def _revoke_action(self, action: Action) -> Action:
        """
        Update the status of the Action to REVOKED.
        """

        _query = gql.gql(
            """
            mutation updateActionMutation($modelId: String!, $status: ActionStatusEnum ) {
                updateAction(input: {modelId: $modelId , status: $status}) {
                    action {
                        modelId
                        status
                        name
                        progress
                    }
                    errors {
                        fields
                        message
                    }
                }
            }
        """
        )

        self._client.execute(
            _query, {"modelId": action.action_id, "status": ActionStatus.REVOKED.value}
        )

    def request_machines(self, machine_count: int):
        """
        Request a minimum number of machines to be online.

        Notes
        -----
        This command is blocking until the specified amount of machines
        have been observed in your environment. It only attempts to ensure
        the requested amount and not necessarily create the same amount if
        the existing machines are already present.

        Parameters
        ----------
        machine_count: int
            The minimum number of machines requested to be online.
        """
        if not isinstance(machine_count, int) or machine_count < 1:
            raise GraphQLClientError(
                "The number of machines requested must be an integer greater than 0."
            )

        if self._request_minimum_number_of_machines(machine_count) > 0:
            _s = "" if machine_count == 1 else "s"
            print(f"Waiting for {machine_count} machine{_s} to be online...")
            self.wait_for_machine_instantiation(machine_count)
        print(f"Requested machines ({machine_count}) are online.")

    def _request_minimum_number_of_machines(self, machine_count: int) -> int:
        """
        Request the minimum number of machines that are to be provisioned.
        """

        _query = gql.gql(
            """
        mutation requestMachines($minimum: Int!, $organizationId: ID!) {
            requestMachines(input: {minimum: $minimum, organizationId: $organizationId}) {
                machineRequested
                errors {
                    fields
                    message
                }
            }
        }
        """
        )
        response = self._client.execute(
            _query,
            {
                "minimum": machine_count,
                "organizationId": self._get_configured_organization().organization_id,
            },
        )

        if response["requestMachines"]["machineRequested"] is None:
            raise GraphQLClientError(response["requestMachines"]["errors"])

        return response["requestMachines"]["machineRequested"]

    @retry(
        wait=wait_fixed(10),
        retry=retry_if_result(
            lambda response: response["online"] < response["requested"]
        ),
    )
    def wait_for_machine_instantiation(self, number_of_machines_requested: int):
        """
        Wait until the requested number of machines are online.
        """

        number_of_machines_online = self.get_machine_status()["online"]

        def machines(count: int) -> str:
            if count == 1:
                return "1 machine"
            return f"{count} machines"

        print(
            f"Current environment: {machines(number_of_machines_online)} online, "
            f"{machines(number_of_machines_requested - number_of_machines_online)} pending."
        )
        return {
            "online": number_of_machines_online,
            "requested": number_of_machines_requested,
        }

    def get_machine_status(self) -> dict[str, int]:
        """
        Return the current state of all machines.
        """
        _query = gql.gql(
            """
            query tenantQuery($organizationId: ID!) {
                tenant(organizationId:$organizationId) {
                    tenant {
                        currentInstances {
                            initializing
                            offline
                            online
                            pending
                            terminating
                            }
                    }
                    errors {
                        message
                    }
                }
            }
            """
        )

        response = self._client.execute(
            _query,
            {"organizationId": self._get_configured_organization().organization_id},
        )
        return response["tenant"]["tenant"]["currentInstances"]

    def get_usage_time(self) -> float:
        """
        Return the total usage time of the machines in the user's cloud environment.
        """
        _query = gql.gql(
            """
            query UsageSummary($organizationId: ID!) {
                tenant(organizationId: $organizationId) {
                    tenant {
                        usageSummary {
                            allocatedComputeSeconds
                            usedComputeSeconds
                            availableComputeSeconds
                        }
                    }
                    errors {
                    message
                    }
                }
            }
            """
        )

        response = self._client.execute(
            _query,
            {"organizationId": self._get_configured_organization().organization_id},
        )
        return response["tenant"]["tenant"]["usageSummary"]

    def shut_down_machines(self) -> dict[str, Any]:
        """
        Shut down all the machines in the user's cloud environment.

        Returns
        -------
        dict[str, Any]
            The response from the server,
            like {'terminateTenant': {'successMessage': '...', 'errors': Any}}
        """
        _query = gql.gql(
            """
        mutation terminateTenant($organizationId: ID!, $organizationSlug: String!) {
            terminateTenant(
            input: {organizationId: $organizationId, organizationSlug: $organizationSlug}
            ) {
                successMessage
                errors {
                    fields
                    message
                }
            }
        }
        """
        )
        return self._client.execute(
            _query,
            {
                "organizationId": self._get_configured_organization().organization_id,
                "organizationSlug": self._get_configured_organization().slug,
            },
        )

    def activity_monitor(
        self,
        limit: int,
        offset: int = 0,
        status: Optional[str] = None,
        only_user_results: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Fetch metadata from previously submitted actions.

        Parameters
        ----------
        limit : int
            The number of actions to fetch.
        offset : int, optional
            The number of recent actions to ignore before starting to fetch.
            Defaults to 0.
        status : str or None, optional
            The filter for action status. Defaults to None.
        only_user_results : bool, optional
            If True, only fetch actions that belong to the user;
            otherwise, fetch actions that belong to the user's organization.
            Defaults to True.

        Returns
        -------
        list[dict[str, Any]]
            Action metadata with one raw JSON-style dictionary per action.
        """
        _query = gql.gql(
            """
            query getActions($limit: Int, $offset: Int, $filterBy: ActionFilter) {
                actions(limit:$limit, offset:$offset, filterBy:$filterBy) {
                    actions {
                        name
                        status
                        modelType
                        progress
                        createdAt
                        updatedAt
                        modelId
                    }
                    errors {
                        message
                    }
                }
            }
        """
        )

        check_argument(limit >= 1, "Limit must be at least 1.", {"limit": limit})
        check_argument(offset >= 0, "Offset must be at least 0.", {"offset": offset})

        filter_by = {}
        if not only_user_results:
            filter_by["organizationSlug"] = self._get_configured_organization().slug
        if status is not None:
            valid_statuses = [status.value for status in ActionStatus]
            check_argument(
                condition=status in valid_statuses,
                description="Status is not valid. "
                "Please choose from a valid status type: "
                f"{valid_statuses}",
                arguments={"status": status},
            )
            filter_by["status"] = {"exact": status}

        response = self._client.execute(
            _query, {"limit": limit, "offset": offset, "filterBy": filter_by}
        )
        return response["actions"]["actions"]


class ParallelCollector:
    """
    Collect tasks to run them in parallel.
    """

    def __init__(self, router: ApiRouter, callback: Optional[Callable[dict, dict]]):
        self._router = router
        self._callback = (lambda x: x.decoded) if callback is None else callback
        self._async_results = []

    def add(self, async_result: Dict[str, Action]) -> None:
        """
        The async result as a dictionary is added for fetching the response later
        when existing the context manager.
        """
        assert len(async_result) == 1
        self._async_results.append(async_result)

    def __enter__(self):
        self._router._parallel_task_collector = self

    def __exit__(self, exc_type, exc_value, traceback):
        self._router._parallel_task_collector = None

        # Do not try to call any functions upon an exception.
        if isinstance(exc_value, Exception):
            return False

        for result in self._async_results:
            action = result.pop("async_result", None)
            assert action is not None
            response = self._router._fetch_action(action)
            if action.action_id != response.action_id:
                raise RuntimeError(
                    f"Got the wrong result of action {response.action_id}, "
                    f"expected to update the result of action {action.action_id}."
                )
            result.update(self._callback(response.result))

        return True
