import logging
import pymupdf
from typing import Type, Optional

from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from langchain_core.tools import ToolException
from codemie_tools.report_portal.report_portal_client import ReportPortalClient
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

CHECK_YOUR_CREDENTIALS_ERROR = "Report Portal client not initialized. Please check your credentials."

PAGE_NUMBER_DESCRIPTION = "Number of page to retrieve. Pass if page.totalPages > 1"

logger = logging.getLogger(__name__)

# Input Models
class GetExtendedLaunchDataInput(BaseModel):
    launch_id: str = Field(description="Launch ID of the launch to export")


class GetExtendedLaunchDataAsRawInput(BaseModel):
    launch_id: str = Field(description="Launch ID of the launch to export")
    format: Optional[str] = Field(default="html", description="Format of the exported data. May be 'pdf' or 'html'")


class GetLaunchDetailsInput(BaseModel):
    launch_id: str = Field(description="Launch ID of the launch to get details for")


class GetAllLaunchesInput(BaseModel):
    page_number: Optional[int] = Field(default=1, description=PAGE_NUMBER_DESCRIPTION)
    page_sort: Optional[str] = Field(default="startTime,number,DESC", description="Sort order for launches. Defaults to 'startTime,number,DESC' if not specified")
    filter_has_composite_attribute: Optional[str] = Field(default=None, description="Composite attribute filter.")


class FindTestItemByIdInput(BaseModel):
    item_id: str = Field(description="Item ID of the item to get details for")


class GetTestItemsForLaunchInput(BaseModel):
    launch_id: str = Field(description="Launch ID of the launch to get test items for")
    page_number: Optional[int] = Field(default=1, description=PAGE_NUMBER_DESCRIPTION)
    status: Optional[str] = Field(default=None, description="Status of the test item")


class GetLogsForTestItemInput(BaseModel):
    item_id: str = Field(description="Item ID of the item to get logs for")
    page_number: Optional[int] = Field(default=1, description=PAGE_NUMBER_DESCRIPTION)


class GetUserInformationInput(BaseModel):
    username: str = Field(description="Username of the user to get information for")


class GetDashboardDataInput(BaseModel):
    dashboard_id: str = Field(description="Dashboard ID of the dashboard to get data for")


class UpdateTestItemInput(BaseModel):
    item_id: str = Field(description="ID of the test item to update")
    status: str = Field(description="New status for the test item. Must be one of: FAILED, PASSED, SKIPPED")
    description: Optional[str] = Field(default="Status updated manually",
                                       description="Description for the status update")


class BaseReportPortalTool(CodeMieTool):
    """Base class for Report Portal tools."""
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    project: Optional[str] = None
    _client: Optional[ReportPortalClient] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_client()

    def _setup_client(self):
        """Set up Report Portal client."""
        if not self.endpoint or not self.api_key or not self.project:
            logger.error("Missing required configuration for Report Portal: endpoint, api_key, or project")
            return
        
        try:
            self._client = ReportPortalClient(endpoint=self.endpoint, project=self.project, api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to connect to Report Portal: {e}")
            return


class GetExtendedLaunchDataTool(BaseReportPortalTool):
    """Tool to get extended launch data from Report Portal."""
    name: str = GET_EXTENDED_LAUNCH_DATA_TOOL.name
    description: str = GET_EXTENDED_LAUNCH_DATA_TOOL.description
    args_schema: Type[BaseModel] = GetExtendedLaunchDataInput

    def execute(self, launch_id: str):
        """Get extended launch data."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)
        
        try:
            format_type = 'html'
            response = self._client.export_specified_launch(launch_id, format_type)

            if response.headers['Content-Type'] in ['application/pdf', 'text/html']:
                with pymupdf.open(stream=response.content, filetype=format) as report:
                    text_content = ''
                    for page_num in range(len(report)):
                        page = report[page_num]
                        text_content += page.get_text()

                    return text_content
            else:
                logger.warning(f"Exported data for launch {launch_id} is in an unsupported format.")
                return None
        except Exception as e:
            logger.error(f"Error getting extended launch data: {str(e)}")
            raise ToolException(f"Error getting extended launch data: {str(e)}")


class GetExtendedLaunchDataAsRawTool(BaseReportPortalTool):
    """Tool to get extended launch data as raw from Report Portal."""
    name: str = GET_EXTENDED_LAUNCH_DATA_AS_RAW_TOOL.name
    description: str = GET_EXTENDED_LAUNCH_DATA_AS_RAW_TOOL.description
    args_schema: Type[BaseModel] = GetExtendedLaunchDataAsRawInput

    def execute(self, launch_id: str, format: str = 'html'):
        """Get extended launch data as raw."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)
        
        try:
            response = self._client.export_specified_launch(launch_id, format)
            if not response.headers.get('Content-Disposition'):
                logger.warning(f"Exported data for launch {launch_id} is empty.")
                return None
            return response.content
        except Exception as e:
            logger.error(f"Error getting extended launch data as raw: {str(e)}")
            raise ToolException(f"Error getting extended launch data as raw: {str(e)}")


class GetLaunchDetailsTool(BaseReportPortalTool):
    """Tool to get launch details from Report Portal."""
    name: str = GET_LAUNCH_DETAILS_TOOL.name
    description: str = GET_LAUNCH_DETAILS_TOOL.description
    args_schema: Type[BaseModel] = GetLaunchDetailsInput

    def execute(self, launch_id: str):
        """Get launch details."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)
        
        try:
            return self._client.get_launch_details(launch_id)
        except Exception as e:
            logger.error(f"Error getting launch details: {str(e)}")
            raise ToolException(f"Error getting launch details: {str(e)}")


class GetAllLaunchesTool(BaseReportPortalTool):
    """Tool to get all launches from Report Portal."""
    name: str = GET_ALL_LAUNCHES_TOOL.name
    description: str = GET_ALL_LAUNCHES_TOOL.description
    args_schema: Type[BaseModel] = GetAllLaunchesInput

    def execute(self, page_number: int = 1, page_sort: str = "startTime,number,DESC", filter_has_composite_attribute: Optional[str] = None):
        """Get all launches."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)
        
        try:
            return self._client.get_all_launches(page_number, page_sort, filter_has_composite_attribute)
        except Exception as e:
            logger.error(f"Error getting all launches: {str(e)}")
            raise ToolException(f"Error getting all launches: {str(e)}")


class FindTestItemByIdTool(BaseReportPortalTool):
    """Tool to find test item by ID from Report Portal."""
    name: str = FIND_TEST_ITEM_BY_ID_TOOL.name
    description: str = FIND_TEST_ITEM_BY_ID_TOOL.description
    args_schema: Type[BaseModel] = FindTestItemByIdInput

    def execute(self, item_id: str):
        """Find test item by ID."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)
        
        try:
            return self._client.find_test_item_by_id(item_id)
        except Exception as e:
            logger.error(f"Error finding test item by ID: {str(e)}")
            raise ToolException(f"Error finding test item by ID: {str(e)}")


class GetTestItemsForLaunchTool(BaseReportPortalTool):
    """Tool to get test items for launch from Report Portal."""
    name: str = GET_TEST_ITEMS_FOR_LAUNCH_TOOL.name
    description: str = GET_TEST_ITEMS_FOR_LAUNCH_TOOL.description
    args_schema: Type[BaseModel] = GetTestItemsForLaunchInput

    def execute(self, launch_id: str, page_number: int = 1, status: str = None) -> dict:
        """Get test items for launch."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)
        
        try:
            return self._client.get_test_items_for_launch(launch_id, page_number, status)
        except Exception as e:
            logger.error(f"Error getting test items for launch: {str(e)}")
            raise ToolException(f"Error getting test items for launch: {str(e)}")


class GetLogsForTestItemTool(BaseReportPortalTool):
    """Tool to get logs for test item from Report Portal."""
    name: str = GET_LOGS_FOR_TEST_ITEM_TOOL.name
    description: str = GET_LOGS_FOR_TEST_ITEM_TOOL.description
    args_schema: Type[BaseModel] = GetLogsForTestItemInput

    def execute(self, item_id: str, page_number: int = 1):
        """Get logs for test item."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)
        
        try:
            return self._client.get_logs_for_test_items(item_id, page_number)
        except Exception as e:
            logger.error(f"Error getting logs for test item: {str(e)}")
            raise ToolException(f"Error getting logs for test item: {str(e)}")


class GetUserInformationTool(BaseReportPortalTool):
    """Tool to get user information from Report Portal."""
    name: str = GET_USER_INFORMATION_TOOL.name
    description: str = GET_USER_INFORMATION_TOOL.description
    args_schema: Type[BaseModel] = GetUserInformationInput

    def execute(self, username: str):
        """Get user information."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)
        
        try:
            return self._client.get_user_information(username)
        except Exception as e:
            logger.error(f"Error getting user information: {str(e)}")
            raise ToolException(f"Error getting user information: {str(e)}")


class GetDashboardDataTool(BaseReportPortalTool):
    """Tool to get dashboard data from Report Portal."""
    name: str = GET_DASHBOARD_DATA_TOOL.name
    description: str = GET_DASHBOARD_DATA_TOOL.description
    args_schema: Type[BaseModel] = GetDashboardDataInput

    def execute(self, dashboard_id: str):
        """Get dashboard data."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)
        
        try:
            return self._client.get_dashboard_data(dashboard_id)
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            raise ToolException(f"Error getting dashboard data: {str(e)}")


class UpdateTestItemTool(BaseReportPortalTool):
    """Tool to update test item status in Report Portal."""
    name: str = UPDATE_TEST_ITEM_TOOL.name
    description: str = UPDATE_TEST_ITEM_TOOL.description
    args_schema: Type[BaseModel] = UpdateTestItemInput

    def execute(self, item_id: str, status: str, description: str = "Status updated manually"):
        """Update test item status."""
        if not self._client:
            raise ToolException(CHECK_YOUR_CREDENTIALS_ERROR)

        # Validate status values
        valid_statuses = ["FAILED", "PASSED", "SKIPPED"]
        if status.upper() not in valid_statuses:
            raise ToolException(f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}")

        try:
            return self._client.update_test_item(item_id, status.upper(), description)
        except Exception as e:
            logger.error(f"Error updating test item: {str(e)}")
            raise ToolException(f"Error updating test item: {str(e)}")
