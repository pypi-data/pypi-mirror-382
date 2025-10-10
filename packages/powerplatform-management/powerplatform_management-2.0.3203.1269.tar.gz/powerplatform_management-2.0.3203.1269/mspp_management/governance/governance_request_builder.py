from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .cross_tenant_connection_reports.cross_tenant_connection_reports_request_builder import CrossTenantConnectionReportsRequestBuilder
    from .rule_based_policies.rule_based_policies_request_builder import RuleBasedPoliciesRequestBuilder

class GovernanceRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /governance
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new GovernanceRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/governance", path_parameters)
    
    @property
    def cross_tenant_connection_reports(self) -> CrossTenantConnectionReportsRequestBuilder:
        """
        The crossTenantConnectionReports property
        """
        from .cross_tenant_connection_reports.cross_tenant_connection_reports_request_builder import CrossTenantConnectionReportsRequestBuilder

        return CrossTenantConnectionReportsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def rule_based_policies(self) -> RuleBasedPoliciesRequestBuilder:
        """
        The ruleBasedPolicies property
        """
        from .rule_based_policies.rule_based_policies_request_builder import RuleBasedPoliciesRequestBuilder

        return RuleBasedPoliciesRequestBuilder(self.request_adapter, self.path_parameters)
    

