from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_environment_group_item_request_builder import WithEnvironmentGroupItemRequestBuilder

class EnvironmentGroupsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /governance/ruleBasedPolicies/environmentGroups
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EnvironmentGroupsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/governance/ruleBasedPolicies/environmentGroups", path_parameters)
    
    def by_environment_group_id(self,environment_group_id: str) -> WithEnvironmentGroupItemRequestBuilder:
        """
        Gets an item from the ApiSdk.governance.ruleBasedPolicies.environmentGroups.item collection
        param environment_group_id: The unique identifier of the environment group.
        Returns: WithEnvironmentGroupItemRequestBuilder
        """
        if environment_group_id is None:
            raise TypeError("environment_group_id cannot be null.")
        from .item.with_environment_group_item_request_builder import WithEnvironmentGroupItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["environmentGroupId"] = environment_group_id
        return WithEnvironmentGroupItemRequestBuilder(self.request_adapter, url_tpl_params)
    

