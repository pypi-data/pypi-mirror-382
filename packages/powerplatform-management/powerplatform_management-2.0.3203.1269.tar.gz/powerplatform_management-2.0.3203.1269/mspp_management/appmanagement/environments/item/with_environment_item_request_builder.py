from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .application_packages.application_packages_request_builder import ApplicationPackagesRequestBuilder
    from .operations.operations_request_builder import OperationsRequestBuilder

class WithEnvironmentItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /appmanagement/environments/{environmentId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithEnvironmentItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/appmanagement/environments/{environmentId}", path_parameters)
    
    @property
    def application_packages(self) -> ApplicationPackagesRequestBuilder:
        """
        The applicationPackages property
        """
        from .application_packages.application_packages_request_builder import ApplicationPackagesRequestBuilder

        return ApplicationPackagesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def operations(self) -> OperationsRequestBuilder:
        """
        The operations property
        """
        from .operations.operations_request_builder import OperationsRequestBuilder

        return OperationsRequestBuilder(self.request_adapter, self.path_parameters)
    

