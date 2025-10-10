from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

@dataclass
class EnvironmentManagementSetting(Parsable):
    # The allowedIpRangeForStorageAccessSignatures property
    allowed_ip_range_for_storage_access_signatures: Optional[str] = None
    # The copilotStudio_CodeInterpreter property
    copilot_studio_code_interpreter: Optional[bool] = None
    # The copilotStudio_ComputerUseAppAllowlist property
    copilot_studio_computer_use_app_allowlist: Optional[str] = None
    # The copilotStudio_ComputerUseCredentialsAllowed property
    copilot_studio_computer_use_credentials_allowed: Optional[bool] = None
    # The copilotStudio_ComputerUseSharedMachines property
    copilot_studio_computer_use_shared_machines: Optional[bool] = None
    # The copilotStudio_ComputerUseWebAllowlist property
    copilot_studio_computer_use_web_allowlist: Optional[str] = None
    # The copilotStudio_ConnectedAgents property
    copilot_studio_connected_agents: Optional[bool] = None
    # The copilotStudio_ConversationAuditLoggingEnabled property
    copilot_studio_conversation_audit_logging_enabled: Optional[bool] = None
    # The d365CustomerService_AIAgents property
    d365_customer_service_a_i_agents: Optional[bool] = None
    # The d365CustomerService_Copilot property
    d365_customer_service_copilot: Optional[bool] = None
    # The enableIpBasedStorageAccessSignatureRule property
    enable_ip_based_storage_access_signature_rule: Optional[bool] = None
    # The id property
    id: Optional[str] = None
    # The ipBasedStorageAccessSignatureMode property
    ip_based_storage_access_signature_mode: Optional[int] = None
    # The loggingEnabledForIpBasedStorageAccessSignature property
    logging_enabled_for_ip_based_storage_access_signature: Optional[bool] = None
    # The powerApps_AllowCodeApps property
    power_apps_allow_code_apps: Optional[bool] = None
    # The powerApps_ChartVisualization property
    power_apps_chart_visualization: Optional[bool] = None
    # The powerApps_CopilotChat property
    power_apps_copilot_chat: Optional[bool] = None
    # The powerApps_EnableFormInsights property
    power_apps_enable_form_insights: Optional[bool] = None
    # The powerApps_FormPredictAutomatic property
    power_apps_form_predict_automatic: Optional[bool] = None
    # The powerApps_FormPredictSmartPaste property
    power_apps_form_predict_smart_paste: Optional[bool] = None
    # The powerApps_NLSearch property
    power_apps_n_l_search: Optional[bool] = None
    # The powerPages_AllowIntelligentFormsCopilotForSites property
    power_pages_allow_intelligent_forms_copilot_for_sites: Optional[str] = None
    # The powerPages_AllowListSummaryCopilotForSites property
    power_pages_allow_list_summary_copilot_for_sites: Optional[str] = None
    # The powerPages_AllowMakerCopilotsForExistingSites property
    power_pages_allow_maker_copilots_for_existing_sites: Optional[str] = None
    # The powerPages_AllowMakerCopilotsForNewSites property
    power_pages_allow_maker_copilots_for_new_sites: Optional[str] = None
    # The powerPages_AllowNonProdPublicSites property
    power_pages_allow_non_prod_public_sites: Optional[str] = None
    # The powerPages_AllowNonProdPublicSites_Exemptions property
    power_pages_allow_non_prod_public_sites_exemptions: Optional[str] = None
    # The powerPages_AllowProDevCopilotsForEnvironment property
    power_pages_allow_pro_dev_copilots_for_environment: Optional[str] = None
    # The powerPages_AllowProDevCopilotsForSites property
    power_pages_allow_pro_dev_copilots_for_sites: Optional[str] = None
    # The powerPages_AllowSearchSummaryCopilotForSites property
    power_pages_allow_search_summary_copilot_for_sites: Optional[str] = None
    # The powerPages_AllowSiteCopilotForSites property
    power_pages_allow_site_copilot_for_sites: Optional[str] = None
    # The powerPages_AllowSummarizationAPICopilotForSites property
    power_pages_allow_summarization_a_p_i_copilot_for_sites: Optional[str] = None
    # The tenantId property
    tenant_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EnvironmentManagementSetting:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EnvironmentManagementSetting
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EnvironmentManagementSetting()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "allowedIpRangeForStorageAccessSignatures": lambda n : setattr(self, 'allowed_ip_range_for_storage_access_signatures', n.get_str_value()),
            "copilotStudio_CodeInterpreter": lambda n : setattr(self, 'copilot_studio_code_interpreter', n.get_bool_value()),
            "copilotStudio_ComputerUseAppAllowlist": lambda n : setattr(self, 'copilot_studio_computer_use_app_allowlist', n.get_str_value()),
            "copilotStudio_ComputerUseCredentialsAllowed": lambda n : setattr(self, 'copilot_studio_computer_use_credentials_allowed', n.get_bool_value()),
            "copilotStudio_ComputerUseSharedMachines": lambda n : setattr(self, 'copilot_studio_computer_use_shared_machines', n.get_bool_value()),
            "copilotStudio_ComputerUseWebAllowlist": lambda n : setattr(self, 'copilot_studio_computer_use_web_allowlist', n.get_str_value()),
            "copilotStudio_ConnectedAgents": lambda n : setattr(self, 'copilot_studio_connected_agents', n.get_bool_value()),
            "copilotStudio_ConversationAuditLoggingEnabled": lambda n : setattr(self, 'copilot_studio_conversation_audit_logging_enabled', n.get_bool_value()),
            "d365CustomerService_AIAgents": lambda n : setattr(self, 'd365_customer_service_a_i_agents', n.get_bool_value()),
            "d365CustomerService_Copilot": lambda n : setattr(self, 'd365_customer_service_copilot', n.get_bool_value()),
            "enableIpBasedStorageAccessSignatureRule": lambda n : setattr(self, 'enable_ip_based_storage_access_signature_rule', n.get_bool_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "ipBasedStorageAccessSignatureMode": lambda n : setattr(self, 'ip_based_storage_access_signature_mode', n.get_int_value()),
            "loggingEnabledForIpBasedStorageAccessSignature": lambda n : setattr(self, 'logging_enabled_for_ip_based_storage_access_signature', n.get_bool_value()),
            "powerApps_AllowCodeApps": lambda n : setattr(self, 'power_apps_allow_code_apps', n.get_bool_value()),
            "powerApps_ChartVisualization": lambda n : setattr(self, 'power_apps_chart_visualization', n.get_bool_value()),
            "powerApps_CopilotChat": lambda n : setattr(self, 'power_apps_copilot_chat', n.get_bool_value()),
            "powerApps_EnableFormInsights": lambda n : setattr(self, 'power_apps_enable_form_insights', n.get_bool_value()),
            "powerApps_FormPredictAutomatic": lambda n : setattr(self, 'power_apps_form_predict_automatic', n.get_bool_value()),
            "powerApps_FormPredictSmartPaste": lambda n : setattr(self, 'power_apps_form_predict_smart_paste', n.get_bool_value()),
            "powerApps_NLSearch": lambda n : setattr(self, 'power_apps_n_l_search', n.get_bool_value()),
            "powerPages_AllowIntelligentFormsCopilotForSites": lambda n : setattr(self, 'power_pages_allow_intelligent_forms_copilot_for_sites', n.get_str_value()),
            "powerPages_AllowListSummaryCopilotForSites": lambda n : setattr(self, 'power_pages_allow_list_summary_copilot_for_sites', n.get_str_value()),
            "powerPages_AllowMakerCopilotsForExistingSites": lambda n : setattr(self, 'power_pages_allow_maker_copilots_for_existing_sites', n.get_str_value()),
            "powerPages_AllowMakerCopilotsForNewSites": lambda n : setattr(self, 'power_pages_allow_maker_copilots_for_new_sites', n.get_str_value()),
            "powerPages_AllowNonProdPublicSites": lambda n : setattr(self, 'power_pages_allow_non_prod_public_sites', n.get_str_value()),
            "powerPages_AllowNonProdPublicSites_Exemptions": lambda n : setattr(self, 'power_pages_allow_non_prod_public_sites_exemptions', n.get_str_value()),
            "powerPages_AllowProDevCopilotsForEnvironment": lambda n : setattr(self, 'power_pages_allow_pro_dev_copilots_for_environment', n.get_str_value()),
            "powerPages_AllowProDevCopilotsForSites": lambda n : setattr(self, 'power_pages_allow_pro_dev_copilots_for_sites', n.get_str_value()),
            "powerPages_AllowSearchSummaryCopilotForSites": lambda n : setattr(self, 'power_pages_allow_search_summary_copilot_for_sites', n.get_str_value()),
            "powerPages_AllowSiteCopilotForSites": lambda n : setattr(self, 'power_pages_allow_site_copilot_for_sites', n.get_str_value()),
            "powerPages_AllowSummarizationAPICopilotForSites": lambda n : setattr(self, 'power_pages_allow_summarization_a_p_i_copilot_for_sites', n.get_str_value()),
            "tenantId": lambda n : setattr(self, 'tenant_id', n.get_uuid_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_str_value("allowedIpRangeForStorageAccessSignatures", self.allowed_ip_range_for_storage_access_signatures)
        writer.write_bool_value("copilotStudio_CodeInterpreter", self.copilot_studio_code_interpreter)
        writer.write_str_value("copilotStudio_ComputerUseAppAllowlist", self.copilot_studio_computer_use_app_allowlist)
        writer.write_bool_value("copilotStudio_ComputerUseCredentialsAllowed", self.copilot_studio_computer_use_credentials_allowed)
        writer.write_bool_value("copilotStudio_ComputerUseSharedMachines", self.copilot_studio_computer_use_shared_machines)
        writer.write_str_value("copilotStudio_ComputerUseWebAllowlist", self.copilot_studio_computer_use_web_allowlist)
        writer.write_bool_value("copilotStudio_ConnectedAgents", self.copilot_studio_connected_agents)
        writer.write_bool_value("copilotStudio_ConversationAuditLoggingEnabled", self.copilot_studio_conversation_audit_logging_enabled)
        writer.write_bool_value("d365CustomerService_AIAgents", self.d365_customer_service_a_i_agents)
        writer.write_bool_value("d365CustomerService_Copilot", self.d365_customer_service_copilot)
        writer.write_bool_value("enableIpBasedStorageAccessSignatureRule", self.enable_ip_based_storage_access_signature_rule)
        writer.write_str_value("id", self.id)
        writer.write_int_value("ipBasedStorageAccessSignatureMode", self.ip_based_storage_access_signature_mode)
        writer.write_bool_value("loggingEnabledForIpBasedStorageAccessSignature", self.logging_enabled_for_ip_based_storage_access_signature)
        writer.write_bool_value("powerApps_AllowCodeApps", self.power_apps_allow_code_apps)
        writer.write_bool_value("powerApps_ChartVisualization", self.power_apps_chart_visualization)
        writer.write_bool_value("powerApps_CopilotChat", self.power_apps_copilot_chat)
        writer.write_bool_value("powerApps_EnableFormInsights", self.power_apps_enable_form_insights)
        writer.write_bool_value("powerApps_FormPredictAutomatic", self.power_apps_form_predict_automatic)
        writer.write_bool_value("powerApps_FormPredictSmartPaste", self.power_apps_form_predict_smart_paste)
        writer.write_bool_value("powerApps_NLSearch", self.power_apps_n_l_search)
        writer.write_str_value("powerPages_AllowIntelligentFormsCopilotForSites", self.power_pages_allow_intelligent_forms_copilot_for_sites)
        writer.write_str_value("powerPages_AllowListSummaryCopilotForSites", self.power_pages_allow_list_summary_copilot_for_sites)
        writer.write_str_value("powerPages_AllowMakerCopilotsForExistingSites", self.power_pages_allow_maker_copilots_for_existing_sites)
        writer.write_str_value("powerPages_AllowMakerCopilotsForNewSites", self.power_pages_allow_maker_copilots_for_new_sites)
        writer.write_str_value("powerPages_AllowNonProdPublicSites", self.power_pages_allow_non_prod_public_sites)
        writer.write_str_value("powerPages_AllowNonProdPublicSites_Exemptions", self.power_pages_allow_non_prod_public_sites_exemptions)
        writer.write_str_value("powerPages_AllowProDevCopilotsForEnvironment", self.power_pages_allow_pro_dev_copilots_for_environment)
        writer.write_str_value("powerPages_AllowProDevCopilotsForSites", self.power_pages_allow_pro_dev_copilots_for_sites)
        writer.write_str_value("powerPages_AllowSearchSummaryCopilotForSites", self.power_pages_allow_search_summary_copilot_for_sites)
        writer.write_str_value("powerPages_AllowSiteCopilotForSites", self.power_pages_allow_site_copilot_for_sites)
        writer.write_str_value("powerPages_AllowSummarizationAPICopilotForSites", self.power_pages_allow_summarization_a_p_i_copilot_for_sites)
        writer.write_uuid_value("tenantId", self.tenant_id)
    

