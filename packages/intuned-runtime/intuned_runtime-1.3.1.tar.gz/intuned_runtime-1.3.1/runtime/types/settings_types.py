from typing import List

from pydantic import BaseModel
from pydantic import Field


class CaptchaSettings(BaseModel):
    enabled: bool = Field(default=False)


class CustomCaptchaSettings(CaptchaSettings):
    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True,
    }

    image_locators: List[str] = Field(alias="imageLocators", default=[])
    submit_locators: List[str] = Field(alias="submitLocators", default=[])
    input_locators: List[str] = Field(alias="inputLocators", default=[])


class TextCaptchaSettings(CaptchaSettings):
    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True,
    }
    label_locators: List[str] = Field(alias="labelLocators", default=[])
    submit_locators: List[str] = Field(alias="submitLocators", default=[])
    input_locators: List[str] = Field(alias="inputLocators", default=[])


class CaptchaSolverSettings(BaseModel):
    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True,
    }

    enabled: bool = Field(default=False)
    cloudflare: CaptchaSettings = Field(default_factory=CaptchaSettings)
    google_recaptcha_v2: CaptchaSettings = Field(alias="googleRecaptchaV2", default_factory=CaptchaSettings)
    google_recaptcha_v3: CaptchaSettings = Field(alias="googleRecaptchaV3", default_factory=CaptchaSettings)
    awscaptcha: CaptchaSettings = Field(default_factory=CaptchaSettings)
    hcaptcha: CaptchaSettings = Field(default_factory=CaptchaSettings)
    funcaptcha: CaptchaSettings = Field(default_factory=CaptchaSettings)
    geetest: CaptchaSettings = Field(default_factory=CaptchaSettings)
    lemin: CaptchaSettings = Field(default_factory=CaptchaSettings)
    custom_captcha: CustomCaptchaSettings = Field(alias="customCaptcha", default_factory=CustomCaptchaSettings)
    text: TextCaptchaSettings = Field(default_factory=TextCaptchaSettings)
    settings: dict[str, int | bool] = Field(
        default={"autoSolve": True, "solveDelay": 2000, "maxRetries": 3, "timeout": 30000}
    )


class IntunedJson(BaseModel):
    model_config = {"populate_by_name": True}

    class _AuthSessions(BaseModel):
        enabled: bool

    auth_sessions: _AuthSessions = Field(alias="authSessions")
    project_name: str | None = Field(alias="projectName", default=None)
    workspace_id: str | None = Field(alias="workspaceId", default=None)
    captcha_solver: CaptchaSolverSettings | None = Field(alias="captchaSolver", default=None)
