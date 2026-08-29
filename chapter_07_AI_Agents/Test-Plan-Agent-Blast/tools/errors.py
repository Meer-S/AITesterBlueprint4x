"""Typed error taxonomy. BR-15: every error names what failed and the one fix."""


class AgentError(Exception):
    """Base. `remedy` is the single action that fixes it."""

    def __init__(self, message: str, remedy: str = ""):
        super().__init__(message)
        self.message = message
        self.remedy = remedy

    def __str__(self):
        return f"{self.message}\n-> {self.remedy}" if self.remedy else self.message


class ConfigError(AgentError):
    pass


class InvalidKeyError(AgentError):
    pass


class JiraError(AgentError):
    pass


class JiraAuthError(JiraError):
    pass


class JiraPermissionError(JiraError):
    pass


class JiraNotFoundError(JiraError):
    pass


class JiraRateLimitError(JiraError):
    pass


class JiraConnectionError(JiraError):
    pass


class LLMError(AgentError):
    pass


class SchemaError(AgentError):
    pass


class RenderError(AgentError):
    pass


class NotPlannableError(AgentError):
    """Not a failure. BR-4: refusing a thin ticket is correct behavior."""

    def __init__(self, message, remedy="", report=None):
        super().__init__(message, remedy)
        self.report = report or {}
