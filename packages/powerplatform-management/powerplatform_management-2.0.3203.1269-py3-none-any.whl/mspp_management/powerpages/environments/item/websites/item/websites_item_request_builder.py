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
    from ......models.error_message import ErrorMessage
    from ......models.website_dto import WebsiteDto
    from .create_waf_rules.create_waf_rules_request_builder import CreateWafRulesRequestBuilder
    from .delete_waf_custom_rules.delete_waf_custom_rules_request_builder import DeleteWafCustomRulesRequestBuilder
    from .disable_waf.disable_waf_request_builder import DisableWafRequestBuilder
    from .enable_waf.enable_waf_request_builder import EnableWafRequestBuilder
    from .get_waf_rules.get_waf_rules_request_builder import GetWafRulesRequestBuilder
    from .get_waf_status.get_waf_status_request_builder import GetWafStatusRequestBuilder
    from .ipaddressrules.ipaddressrules_request_builder import IpaddressrulesRequestBuilder
    from .restart.restart_request_builder import RestartRequestBuilder
    from .scan.scan_request_builder import ScanRequestBuilder
    from .set_portal_bootstrap_v5_enabled.set_portal_bootstrap_v5_enabled_request_builder import SetPortalBootstrapV5EnabledRequestBuilder
    from .set_portal_data_model_version.set_portal_data_model_version_request_builder import SetPortalDataModelVersionRequestBuilder
    from .start.start_request_builder import StartRequestBuilder
    from .stop.stop_request_builder import StopRequestBuilder
    from .update_portal_security_group.update_portal_security_group_request_builder import UpdatePortalSecurityGroupRequestBuilder
    from .update_site_visibility.update_site_visibility_request_builder import UpdateSiteVisibilityRequestBuilder

class WebsitesItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powerpages/environments/{environmentId}/websites/{id}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WebsitesItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powerpages/environments/{environmentId}/websites/{id}?api-version={api%2Dversion}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[WebsitesItemRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Trigger the deletion of a website by specifying the website ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ......models.error_message import ErrorMessage

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ErrorMessage,
            "401": ErrorMessage,
            "404": ErrorMessage,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WebsitesItemRequestBuilderGetQueryParameters]] = None) -> Optional[WebsiteDto]:
        """
        Get website details using a specified website ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[WebsiteDto]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ......models.error_message import ErrorMessage

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ErrorMessage,
            "401": ErrorMessage,
            "404": ErrorMessage,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.website_dto import WebsiteDto

        return await self.request_adapter.send_async(request_info, WebsiteDto, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[WebsitesItemRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Trigger the deletion of a website by specifying the website ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WebsitesItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get website details using a specified website ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> WebsitesItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WebsitesItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WebsitesItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def create_waf_rules(self) -> CreateWafRulesRequestBuilder:
        """
        The createWafRules property
        """
        from .create_waf_rules.create_waf_rules_request_builder import CreateWafRulesRequestBuilder

        return CreateWafRulesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def delete_waf_custom_rules(self) -> DeleteWafCustomRulesRequestBuilder:
        """
        The deleteWafCustomRules property
        """
        from .delete_waf_custom_rules.delete_waf_custom_rules_request_builder import DeleteWafCustomRulesRequestBuilder

        return DeleteWafCustomRulesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def disable_waf(self) -> DisableWafRequestBuilder:
        """
        The disableWaf property
        """
        from .disable_waf.disable_waf_request_builder import DisableWafRequestBuilder

        return DisableWafRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def enable_waf(self) -> EnableWafRequestBuilder:
        """
        The enableWaf property
        """
        from .enable_waf.enable_waf_request_builder import EnableWafRequestBuilder

        return EnableWafRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def get_waf_rules(self) -> GetWafRulesRequestBuilder:
        """
        The getWafRules property
        """
        from .get_waf_rules.get_waf_rules_request_builder import GetWafRulesRequestBuilder

        return GetWafRulesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def get_waf_status(self) -> GetWafStatusRequestBuilder:
        """
        The getWafStatus property
        """
        from .get_waf_status.get_waf_status_request_builder import GetWafStatusRequestBuilder

        return GetWafStatusRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def ipaddressrules(self) -> IpaddressrulesRequestBuilder:
        """
        The ipaddressrules property
        """
        from .ipaddressrules.ipaddressrules_request_builder import IpaddressrulesRequestBuilder

        return IpaddressrulesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def restart(self) -> RestartRequestBuilder:
        """
        The restart property
        """
        from .restart.restart_request_builder import RestartRequestBuilder

        return RestartRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def scan(self) -> ScanRequestBuilder:
        """
        The scan property
        """
        from .scan.scan_request_builder import ScanRequestBuilder

        return ScanRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def set_portal_bootstrap_v5_enabled(self) -> SetPortalBootstrapV5EnabledRequestBuilder:
        """
        The SetPortalBootstrapV5Enabled property
        """
        from .set_portal_bootstrap_v5_enabled.set_portal_bootstrap_v5_enabled_request_builder import SetPortalBootstrapV5EnabledRequestBuilder

        return SetPortalBootstrapV5EnabledRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def set_portal_data_model_version(self) -> SetPortalDataModelVersionRequestBuilder:
        """
        The setPortalDataModelVersion property
        """
        from .set_portal_data_model_version.set_portal_data_model_version_request_builder import SetPortalDataModelVersionRequestBuilder

        return SetPortalDataModelVersionRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def start(self) -> StartRequestBuilder:
        """
        The start property
        """
        from .start.start_request_builder import StartRequestBuilder

        return StartRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def stop(self) -> StopRequestBuilder:
        """
        The stop property
        """
        from .stop.stop_request_builder import StopRequestBuilder

        return StopRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def update_portal_security_group(self) -> UpdatePortalSecurityGroupRequestBuilder:
        """
        The updatePortalSecurityGroup property
        """
        from .update_portal_security_group.update_portal_security_group_request_builder import UpdatePortalSecurityGroupRequestBuilder

        return UpdatePortalSecurityGroupRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def update_site_visibility(self) -> UpdateSiteVisibilityRequestBuilder:
        """
        The updateSiteVisibility property
        """
        from .update_site_visibility.update_site_visibility_request_builder import UpdateSiteVisibilityRequestBuilder

        return UpdateSiteVisibilityRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WebsitesItemRequestBuilderDeleteQueryParameters():
        """
        Trigger the deletion of a website by specifying the website ID.
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
    class WebsitesItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[WebsitesItemRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WebsitesItemRequestBuilderGetQueryParameters():
        """
        Get website details using a specified website ID.
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
    class WebsitesItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WebsitesItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

