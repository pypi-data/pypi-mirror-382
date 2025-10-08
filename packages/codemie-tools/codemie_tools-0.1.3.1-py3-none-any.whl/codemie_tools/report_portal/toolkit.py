from typing import Dict, Any, List, Tuple

from pydantic import BaseModel, Field

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.report_portal.report_portal_client import ReportPortalClient
from codemie_tools.report_portal.tools import (
    GetExtendedLaunchDataTool,
    GetExtendedLaunchDataAsRawTool,
    GetLaunchDetailsTool,
    GetAllLaunchesTool,
    FindTestItemByIdTool,
    GetTestItemsForLaunchTool,
    GetLogsForTestItemTool,
    GetUserInformationTool,
    GetDashboardDataTool,
    UpdateTestItemTool
)
from codemie_tools.report_portal.tools_vars import (
    GET_EXTENDED_LAUNCH_DATA_TOOL,
    GET_EXTENDED_LAUNCH_DATA_AS_RAW_TOOL,
    GET_LAUNCH_DETAILS_TOOL,
    GET_ALL_LAUNCHES_TOOL,
    FIND_TEST_ITEM_BY_ID_TOOL,
    GET_TEST_ITEMS_FOR_LAUNCH_TOOL,
    GET_LOGS_FOR_TEST_ITEM_TOOL,
    GET_USER_INFORMATION_TOOL,
    GET_DASHBOARD_DATA_TOOL,
    UPDATE_TEST_ITEM_TOOL
)
from codemie_tools.base.utils import humanize_error


class ReportPortalConfig(BaseModel):
    url: str = Field(description="Report Portal endpoint URL")
    api_key: str = Field(description="Report Portal API key")
    project: str = Field(description="Report Portal project name")


class ReportPortalToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.REPORT_PORTAL
    tools: List[Tool] = [
        Tool.from_metadata(GET_EXTENDED_LAUNCH_DATA_TOOL),
        Tool.from_metadata(GET_EXTENDED_LAUNCH_DATA_AS_RAW_TOOL),
        Tool.from_metadata(GET_LAUNCH_DETAILS_TOOL),
        Tool.from_metadata(GET_ALL_LAUNCHES_TOOL),
        Tool.from_metadata(FIND_TEST_ITEM_BY_ID_TOOL),
        Tool.from_metadata(GET_TEST_ITEMS_FOR_LAUNCH_TOOL),
        Tool.from_metadata(GET_LOGS_FOR_TEST_ITEM_TOOL),
        Tool.from_metadata(GET_USER_INFORMATION_TOOL),
        Tool.from_metadata(GET_DASHBOARD_DATA_TOOL),
        Tool.from_metadata(UPDATE_TEST_ITEM_TOOL),
    ]


class ReportPortalToolkit(BaseToolkit):
    rp_config: ReportPortalConfig

    @classmethod
    def get_tools_ui_info(cls):
        return ToolKit(
            toolkit=ToolSet.REPORT_PORTAL,
            tools=[
                Tool.from_metadata(GET_EXTENDED_LAUNCH_DATA_AS_RAW_TOOL),
                Tool.from_metadata(GET_LAUNCH_DETAILS_TOOL),
                Tool.from_metadata(GET_ALL_LAUNCHES_TOOL),
                Tool.from_metadata(FIND_TEST_ITEM_BY_ID_TOOL),
                Tool.from_metadata(GET_TEST_ITEMS_FOR_LAUNCH_TOOL),
                Tool.from_metadata(GET_LOGS_FOR_TEST_ITEM_TOOL),
                Tool.from_metadata(GET_USER_INFORMATION_TOOL),
                Tool.from_metadata(GET_DASHBOARD_DATA_TOOL),
                Tool.from_metadata(UPDATE_TEST_ITEM_TOOL),
            ],
            settings_config=True
        ).model_dump()

    def health_check(self) -> Tuple[bool, str]:
        """Check if Report Portal is accessible with current configuration."""
        try:
            client = ReportPortalClient(
                endpoint=self.rp_config.url,
                project=self.rp_config.project,
                api_key=self.rp_config.api_key
            )
            # Try a simple API call to verify connectivity
            client.get_all_launches(page_number=1)
            return True, ""
        except Exception as e:
            return False, humanize_error(e)


    def get_tools(self) -> list:
        """Get all available Report Portal tools."""
        tools = [
            GetExtendedLaunchDataAsRawTool(
                endpoint=self.rp_config.url,
                api_key=self.rp_config.api_key,
                project=self.rp_config.project
            ),
            GetLaunchDetailsTool(
                endpoint=self.rp_config.url,
                api_key=self.rp_config.api_key,
                project=self.rp_config.project
            ),
            GetAllLaunchesTool(
                endpoint=self.rp_config.url,
                api_key=self.rp_config.api_key,
                project=self.rp_config.project
            ),
            FindTestItemByIdTool(
                endpoint=self.rp_config.url,
                api_key=self.rp_config.api_key,
                project=self.rp_config.project
            ),
            GetTestItemsForLaunchTool(
                endpoint=self.rp_config.url,
                api_key=self.rp_config.api_key,
                project=self.rp_config.project
            ),
            GetLogsForTestItemTool(
                endpoint=self.rp_config.url,
                api_key=self.rp_config.api_key,
                project=self.rp_config.project
            ),
            GetUserInformationTool(
                endpoint=self.rp_config.url,
                api_key=self.rp_config.api_key,
                project=self.rp_config.project
            ),
            GetDashboardDataTool(
                endpoint=self.rp_config.url,
                api_key=self.rp_config.api_key,
                project=self.rp_config.project
            ),
            UpdateTestItemTool(
                endpoint=self.rp_config.url,
                api_key=self.rp_config.api_key,
                project=self.rp_config.project
            )
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        """Create toolkit instance with configuration."""
        rp_config = ReportPortalConfig(**configs)
        return ReportPortalToolkit(rp_config=rp_config)