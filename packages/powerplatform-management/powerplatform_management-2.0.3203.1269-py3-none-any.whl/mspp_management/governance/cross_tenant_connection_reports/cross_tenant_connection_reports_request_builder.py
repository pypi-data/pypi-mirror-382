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
    from ...models.cross_tenant_connection_report import CrossTenantConnectionReport
    from ...models.cross_tenant_connection_reports_response_with_odata_continuation import CrossTenantConnectionReportsResponseWithOdataContinuation
    from .item.with_report_item_request_builder import WithReportItemRequestBuilder

class CrossTenantConnectionReportsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /governance/crossTenantConnectionReports
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new CrossTenantConnectionReportsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/governance/crossTenantConnectionReports?api-version={api%2Dversion}", path_parameters)
    
    def by_report_id(self,report_id: str) -> WithReportItemRequestBuilder:
        """
        Gets an item from the ApiSdk.governance.crossTenantConnectionReports.item collection
        param report_id: The report ID.
        Returns: WithReportItemRequestBuilder
        """
        if report_id is None:
            raise TypeError("report_id cannot be null.")
        from .item.with_report_item_request_builder import WithReportItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["reportId"] = report_id
        return WithReportItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[CrossTenantConnectionReportsRequestBuilderGetQueryParameters]] = None) -> Optional[CrossTenantConnectionReportsResponseWithOdataContinuation]:
        """
        List cross-tenant connection reports for a tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[CrossTenantConnectionReportsResponseWithOdataContinuation]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.cross_tenant_connection_reports_response_with_odata_continuation import CrossTenantConnectionReportsResponseWithOdataContinuation

        return await self.request_adapter.send_async(request_info, CrossTenantConnectionReportsResponseWithOdataContinuation, None)
    
    async def post(self,request_configuration: Optional[RequestConfiguration[CrossTenantConnectionReportsRequestBuilderPostQueryParameters]] = None) -> Optional[CrossTenantConnectionReport]:
        """
        Generate or fetch a cross-tenant connection report.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[CrossTenantConnectionReport]
        """
        request_info = self.to_post_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.cross_tenant_connection_report import CrossTenantConnectionReport

        return await self.request_adapter.send_async(request_info, CrossTenantConnectionReport, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[CrossTenantConnectionReportsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        List cross-tenant connection reports for a tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,request_configuration: Optional[RequestConfiguration[CrossTenantConnectionReportsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Generate or fetch a cross-tenant connection report.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> CrossTenantConnectionReportsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: CrossTenantConnectionReportsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return CrossTenantConnectionReportsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class CrossTenantConnectionReportsRequestBuilderGetQueryParameters():
        """
        List cross-tenant connection reports for a tenant.
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
    class CrossTenantConnectionReportsRequestBuilderGetRequestConfiguration(RequestConfiguration[CrossTenantConnectionReportsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class CrossTenantConnectionReportsRequestBuilderPostQueryParameters():
        """
        Generate or fetch a cross-tenant connection report.
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
    class CrossTenantConnectionReportsRequestBuilderPostRequestConfiguration(RequestConfiguration[CrossTenantConnectionReportsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

