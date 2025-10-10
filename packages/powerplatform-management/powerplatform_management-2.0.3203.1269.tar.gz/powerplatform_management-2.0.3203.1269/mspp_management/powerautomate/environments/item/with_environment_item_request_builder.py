from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .cloud_flows.cloud_flows_request_builder import CloudFlowsRequestBuilder
    from .flow_actions.flow_actions_request_builder import FlowActionsRequestBuilder
    from .flow_runs.flow_runs_request_builder import FlowRunsRequestBuilder

class WithEnvironmentItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powerautomate/environments/{environmentId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithEnvironmentItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powerautomate/environments/{environmentId}", path_parameters)
    
    @property
    def cloud_flows(self) -> CloudFlowsRequestBuilder:
        """
        The cloudFlows property
        """
        from .cloud_flows.cloud_flows_request_builder import CloudFlowsRequestBuilder

        return CloudFlowsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def flow_actions(self) -> FlowActionsRequestBuilder:
        """
        The flowActions property
        """
        from .flow_actions.flow_actions_request_builder import FlowActionsRequestBuilder

        return FlowActionsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def flow_runs(self) -> FlowRunsRequestBuilder:
        """
        The flowRuns property
        """
        from .flow_runs.flow_runs_request_builder import FlowRunsRequestBuilder

        return FlowRunsRequestBuilder(self.request_adapter, self.path_parameters)
    

