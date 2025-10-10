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
    from ...models.role_assignment_request import RoleAssignmentRequest
    from ...models.role_assignment_response import RoleAssignmentResponse
    from .item.with_role_assignment_item_request_builder import WithRoleAssignmentItemRequestBuilder

class RoleAssignmentsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /authorization/roleAssignments
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new RoleAssignmentsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/authorization/roleAssignments?api-version={api%2Dversion}", path_parameters)
    
    def by_role_assignment_id(self,role_assignment_id: str) -> WithRoleAssignmentItemRequestBuilder:
        """
        Gets an item from the ApiSdk.authorization.roleAssignments.item collection
        param role_assignment_id: The unique identifier of the role assignment.
        Returns: WithRoleAssignmentItemRequestBuilder
        """
        if role_assignment_id is None:
            raise TypeError("role_assignment_id cannot be null.")
        from .item.with_role_assignment_item_request_builder import WithRoleAssignmentItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["roleAssignmentId"] = role_assignment_id
        return WithRoleAssignmentItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[RoleAssignmentsRequestBuilderGetQueryParameters]] = None) -> Optional[RoleAssignmentResponse]:
        """
        Retrieves a list of role assignments. PRIVATE PREVIEW https://aka.ms/PowerPlatform/RBAC .
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[RoleAssignmentResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.role_assignment_response import RoleAssignmentResponse

        return await self.request_adapter.send_async(request_info, RoleAssignmentResponse, None)
    
    async def post(self,body: RoleAssignmentRequest, request_configuration: Optional[RequestConfiguration[RoleAssignmentsRequestBuilderPostQueryParameters]] = None) -> Optional[RoleAssignmentResponse]:
        """
        Creates a new role assignment. PRIVATE PREVIEW https://aka.ms/PowerPlatform/RBAC .
        param body: Request to assign a role to a principal.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[RoleAssignmentResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.role_assignment_response import RoleAssignmentResponse

        return await self.request_adapter.send_async(request_info, RoleAssignmentResponse, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[RoleAssignmentsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Retrieves a list of role assignments. PRIVATE PREVIEW https://aka.ms/PowerPlatform/RBAC .
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: RoleAssignmentRequest, request_configuration: Optional[RequestConfiguration[RoleAssignmentsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Creates a new role assignment. PRIVATE PREVIEW https://aka.ms/PowerPlatform/RBAC .
        param body: Request to assign a role to a principal.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> RoleAssignmentsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: RoleAssignmentsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return RoleAssignmentsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class RoleAssignmentsRequestBuilderGetQueryParameters():
        """
        Retrieves a list of role assignments. PRIVATE PREVIEW https://aka.ms/PowerPlatform/RBAC .
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
    class RoleAssignmentsRequestBuilderGetRequestConfiguration(RequestConfiguration[RoleAssignmentsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class RoleAssignmentsRequestBuilderPostQueryParameters():
        """
        Creates a new role assignment. PRIVATE PREVIEW https://aka.ms/PowerPlatform/RBAC .
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
    class RoleAssignmentsRequestBuilderPostRequestConfiguration(RequestConfiguration[RoleAssignmentsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

