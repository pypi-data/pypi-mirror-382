from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from ....models.problem_details import ProblemDetails
    from ....models.storage_warning_thresholds_document import StorageWarningThresholdsDocument
    from .item.with_entity_name_item_request_builder import WithEntityNameItemRequestBuilder

class WithStorageCategoryItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/storageWarning/{storageCategory}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithStorageCategoryItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/storageWarning/{storageCategory}?api-version={api%2Dversion}", path_parameters)
    
    def by_entity_name(self,entity_name: str) -> WithEntityNameItemRequestBuilder:
        """
        Gets an item from the ApiSdk.licensing.storageWarning.item.item collection
        param entity_name: The name of the entity.
        Returns: WithEntityNameItemRequestBuilder
        """
        if entity_name is None:
            raise TypeError("entity_name cannot be null.")
        from .item.with_entity_name_item_request_builder import WithEntityNameItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["entityName"] = entity_name
        return WithEntityNameItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithStorageCategoryItemRequestBuilderGetQueryParameters]] = None) -> Optional[list[StorageWarningThresholdsDocument]]:
        """
        Storage warning thresholds filtered by category.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[StorageWarningThresholdsDocument]]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "404": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.storage_warning_thresholds_document import StorageWarningThresholdsDocument

        return await self.request_adapter.send_collection_async(request_info, StorageWarningThresholdsDocument, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithStorageCategoryItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Storage warning thresholds filtered by category.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> WithStorageCategoryItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithStorageCategoryItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithStorageCategoryItemRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class WithStorageCategoryItemRequestBuilderGetQueryParameters():
        """
        Storage warning thresholds filtered by category.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "api_version":
                return "api%2Dversion"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

    
    @dataclass
    class WithStorageCategoryItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithStorageCategoryItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

