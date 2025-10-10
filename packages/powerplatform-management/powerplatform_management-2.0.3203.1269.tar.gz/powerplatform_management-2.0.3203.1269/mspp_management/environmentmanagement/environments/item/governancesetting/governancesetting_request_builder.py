from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .disablemanaged.disablemanaged_request_builder import DisablemanagedRequestBuilder
    from .enablemanaged.enablemanaged_request_builder import EnablemanagedRequestBuilder

class GovernancesettingRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /environmentmanagement/environments/{environment-id}/governancesetting
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new GovernancesettingRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/environmentmanagement/environments/{environment%2Did}/governancesetting", path_parameters)
    
    @property
    def disablemanaged(self) -> DisablemanagedRequestBuilder:
        """
        The disablemanaged property
        """
        from .disablemanaged.disablemanaged_request_builder import DisablemanagedRequestBuilder

        return DisablemanagedRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def enablemanaged(self) -> EnablemanagedRequestBuilder:
        """
        The enablemanaged property
        """
        from .enablemanaged.enablemanaged_request_builder import EnablemanagedRequestBuilder

        return EnablemanagedRequestBuilder(self.request_adapter, self.path_parameters)
    

