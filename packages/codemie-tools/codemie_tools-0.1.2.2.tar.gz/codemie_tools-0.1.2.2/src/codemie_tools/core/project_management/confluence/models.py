from typing import Optional, Dict, Any

from pydantic import model_validator, Field

from codemie_tools.base.models import CodeMieToolConfig

class ConfluenceConfig(CodeMieToolConfig):
    url: str = Field(
        description="URL to your Confluence instance, e.g. http://confluence.example.com/",
        json_schema_extra={"placeholder": "https://confluence.example.com/"}
    )
    username: Optional[str] = Field(
        default=None,
        description="Username/email for Confluence (Required for Confluence Cloud)",
        json_schema_extra={"placeholder": "user@example.com"}
    )
    token: str = Field(
        description="API Access Token/ApiKey for authentication.",
        json_schema_extra={
            "placeholder": "Token/ApiKey",
            "sensitive": True,
            "help": "https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html"
        }
    )
    cloud: Optional[bool] = Field(
        default=False,
        description="Is this a Confluence Cloud instance? Toggle on if using Atlassian Cloud"
    )

    @model_validator(mode='before')
    def validate_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = ['url', 'token']
        for field in required_fields:
            if field not in values or not values[field]:
                raise ValueError(f"{field} is a required field and must be provided.")

        if "is_cloud" in values:
            # Special handling for creating model from UI. is_cloud field is passed and should be passed to cloud
            values["cloud"] = values.pop("is_cloud")
        return values
