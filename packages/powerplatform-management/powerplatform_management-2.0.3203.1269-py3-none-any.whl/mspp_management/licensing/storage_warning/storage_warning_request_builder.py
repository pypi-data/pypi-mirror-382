from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .get_all_storage_warnings.get_all_storage_warnings_request_builder import GetAllStorageWarningsRequestBuilder
    from .item.with_storage_category_item_request_builder import WithStorageCategoryItemRequestBuilder

class StorageWarningRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/storageWarning
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new StorageWarningRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/storageWarning", path_parameters)
    
    def by_storage_category(self,storage_category: str) -> WithStorageCategoryItemRequestBuilder:
        """
        Gets an item from the ApiSdk.licensing.storageWarning.item collection
        param storage_category: The storage category value.
        Returns: WithStorageCategoryItemRequestBuilder
        """
        if storage_category is None:
            raise TypeError("storage_category cannot be null.")
        from .item.with_storage_category_item_request_builder import WithStorageCategoryItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["storageCategory"] = storage_category
        return WithStorageCategoryItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def get_all_storage_warnings(self) -> GetAllStorageWarningsRequestBuilder:
        """
        The getAllStorageWarnings property
        """
        from .get_all_storage_warnings.get_all_storage_warnings_request_builder import GetAllStorageWarningsRequestBuilder

        return GetAllStorageWarningsRequestBuilder(self.request_adapter, self.path_parameters)
    

