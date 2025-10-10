from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .environments.environments_request_builder import EnvironmentsRequestBuilder
    from .environment_groups.environment_groups_request_builder import EnvironmentGroupsRequestBuilder
    from .environment_group_operations.environment_group_operations_request_builder import EnvironmentGroupOperationsRequestBuilder
    from .operations.operations_request_builder import OperationsRequestBuilder

class EnvironmentmanagementRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /environmentmanagement
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EnvironmentmanagementRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/environmentmanagement", path_parameters)
    
    @property
    def environment_group_operations(self) -> EnvironmentGroupOperationsRequestBuilder:
        """
        The environmentGroupOperations property
        """
        from .environment_group_operations.environment_group_operations_request_builder import EnvironmentGroupOperationsRequestBuilder

        return EnvironmentGroupOperationsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def environment_groups(self) -> EnvironmentGroupsRequestBuilder:
        """
        The environmentGroups property
        """
        from .environment_groups.environment_groups_request_builder import EnvironmentGroupsRequestBuilder

        return EnvironmentGroupsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def environments(self) -> EnvironmentsRequestBuilder:
        """
        The environments property
        """
        from .environments.environments_request_builder import EnvironmentsRequestBuilder

        return EnvironmentsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def operations(self) -> OperationsRequestBuilder:
        """
        The operations property
        """
        from .operations.operations_request_builder import OperationsRequestBuilder

        return OperationsRequestBuilder(self.request_adapter, self.path_parameters)
    

