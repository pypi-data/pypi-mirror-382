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
    from ....models.environment_response import EnvironmentResponse
    from ....models.validation_response import ValidationResponse
    from .backups.backups_request_builder import BackupsRequestBuilder
    from .business_continuity_state_full_snapshot.business_continuity_state_full_snapshot_request_builder import BusinessContinuityStateFullSnapshotRequestBuilder
    from .copy.copy_request_builder import CopyRequestBuilder
    from .copy_candidates.copy_candidates_request_builder import CopyCandidatesRequestBuilder
    from .disable.disable_request_builder import DisableRequestBuilder
    from .disable_disaster_recovery.disable_disaster_recovery_request_builder import DisableDisasterRecoveryRequestBuilder
    from .disaster_recovery_drill.disaster_recovery_drill_request_builder import DisasterRecoveryDrillRequestBuilder
    from .enable.enable_request_builder import EnableRequestBuilder
    from .enable_disaster_recovery.enable_disaster_recovery_request_builder import EnableDisasterRecoveryRequestBuilder
    from .force_failover.force_failover_request_builder import ForceFailoverRequestBuilder
    from .governancesetting.governancesetting_request_builder import GovernancesettingRequestBuilder
    from .modify_sku.modify_sku_request_builder import ModifySkuRequestBuilder
    from .operations.operations_request_builder import OperationsRequestBuilder
    from .recover.recover_request_builder import RecoverRequestBuilder
    from .restore.restore_request_builder import RestoreRequestBuilder
    from .restore_candidates.restore_candidates_request_builder import RestoreCandidatesRequestBuilder
    from .settings.settings_request_builder import SettingsRequestBuilder

class EnvironmentItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /environmentmanagement/environments/{environment-id}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EnvironmentItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/environmentmanagement/environments/{environment%2Did}?api-version={api%2Dversion}{&ValidateOnly*,ValidateProperties*}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[EnvironmentItemRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Deletes the specified environment by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ....models.validation_response import ValidationResponse

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ValidationResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[EnvironmentItemRequestBuilderGetQueryParameters]] = None) -> Optional[EnvironmentResponse]:
        """
        Retrieves a single environment by ID (preview).
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[EnvironmentResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.environment_response import EnvironmentResponse

        return await self.request_adapter.send_async(request_info, EnvironmentResponse, None)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[EnvironmentItemRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Deletes the specified environment by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json, text/plain;q=0.9")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[EnvironmentItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Retrieves a single environment by ID (preview).
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, '{+baseurl}/environmentmanagement/environments/{environment%2Did}?api-version={api%2Dversion}', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> EnvironmentItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: EnvironmentItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return EnvironmentItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def backups(self) -> BackupsRequestBuilder:
        """
        The backups property
        """
        from .backups.backups_request_builder import BackupsRequestBuilder

        return BackupsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def business_continuity_state_full_snapshot(self) -> BusinessContinuityStateFullSnapshotRequestBuilder:
        """
        The businessContinuityStateFullSnapshot property
        """
        from .business_continuity_state_full_snapshot.business_continuity_state_full_snapshot_request_builder import BusinessContinuityStateFullSnapshotRequestBuilder

        return BusinessContinuityStateFullSnapshotRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def copy(self) -> CopyRequestBuilder:
        """
        The copy property
        """
        from .copy.copy_request_builder import CopyRequestBuilder

        return CopyRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def copy_candidates(self) -> CopyCandidatesRequestBuilder:
        """
        The copyCandidates property
        """
        from .copy_candidates.copy_candidates_request_builder import CopyCandidatesRequestBuilder

        return CopyCandidatesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def disable(self) -> DisableRequestBuilder:
        """
        The Disable property
        """
        from .disable.disable_request_builder import DisableRequestBuilder

        return DisableRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def disable_disaster_recovery(self) -> DisableDisasterRecoveryRequestBuilder:
        """
        The disableDisasterRecovery property
        """
        from .disable_disaster_recovery.disable_disaster_recovery_request_builder import DisableDisasterRecoveryRequestBuilder

        return DisableDisasterRecoveryRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def disaster_recovery_drill(self) -> DisasterRecoveryDrillRequestBuilder:
        """
        The disasterRecoveryDrill property
        """
        from .disaster_recovery_drill.disaster_recovery_drill_request_builder import DisasterRecoveryDrillRequestBuilder

        return DisasterRecoveryDrillRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def enable(self) -> EnableRequestBuilder:
        """
        The Enable property
        """
        from .enable.enable_request_builder import EnableRequestBuilder

        return EnableRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def enable_disaster_recovery(self) -> EnableDisasterRecoveryRequestBuilder:
        """
        The enableDisasterRecovery property
        """
        from .enable_disaster_recovery.enable_disaster_recovery_request_builder import EnableDisasterRecoveryRequestBuilder

        return EnableDisasterRecoveryRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def force_failover(self) -> ForceFailoverRequestBuilder:
        """
        The forceFailover property
        """
        from .force_failover.force_failover_request_builder import ForceFailoverRequestBuilder

        return ForceFailoverRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def governancesetting(self) -> GovernancesettingRequestBuilder:
        """
        The governancesetting property
        """
        from .governancesetting.governancesetting_request_builder import GovernancesettingRequestBuilder

        return GovernancesettingRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def modify_sku(self) -> ModifySkuRequestBuilder:
        """
        The modifySku property
        """
        from .modify_sku.modify_sku_request_builder import ModifySkuRequestBuilder

        return ModifySkuRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def operations(self) -> OperationsRequestBuilder:
        """
        The operations property
        """
        from .operations.operations_request_builder import OperationsRequestBuilder

        return OperationsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def recover(self) -> RecoverRequestBuilder:
        """
        The recover property
        """
        from .recover.recover_request_builder import RecoverRequestBuilder

        return RecoverRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def restore(self) -> RestoreRequestBuilder:
        """
        The Restore property
        """
        from .restore.restore_request_builder import RestoreRequestBuilder

        return RestoreRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def restore_candidates(self) -> RestoreCandidatesRequestBuilder:
        """
        The restoreCandidates property
        """
        from .restore_candidates.restore_candidates_request_builder import RestoreCandidatesRequestBuilder

        return RestoreCandidatesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def settings(self) -> SettingsRequestBuilder:
        """
        The settings property
        """
        from .settings.settings_request_builder import SettingsRequestBuilder

        return SettingsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class EnvironmentItemRequestBuilderDeleteQueryParameters():
        """
        Deletes the specified environment by ID.
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
            if original_name == "validate_only":
                return "ValidateOnly"
            if original_name == "validate_properties":
                return "ValidateProperties"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # The value which indicates whether the operation is a validated only request.Examples:    validateOnly=true with validateProperties non-empty: Validate only the listed properties, ignoring others even if present in the body.    validateOnly=true with empty/absent validateProperties: Validate the entire body (equivalent to full validation).    validateOnly=false or omitted: Process the full request(validate and execute).
        validate_only: Optional[bool] = None

        # The value which indicates what properties should be validated. Need to work together with ValidateOnly.Properties should be separated by ','.Example: "property1,property2,property3".
        validate_properties: Optional[str] = None

    
    @dataclass
    class EnvironmentItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[EnvironmentItemRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class EnvironmentItemRequestBuilderGetQueryParameters():
        """
        Retrieves a single environment by ID (preview).
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
    class EnvironmentItemRequestBuilderGetRequestConfiguration(RequestConfiguration[EnvironmentItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

