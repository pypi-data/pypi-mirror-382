"""
Reading settings from environment variables and providing a settings object
for the application configuration.
"""

import sys
from httpx import URL
from io import StringIO
from pathlib import Path
from typing import Annotated, Any, Dict, List, Literal, Optional, Set, Union
import threading
import warnings

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml

from mcp_agent.agents.agent_spec import AgentSpec


class MCPServerAuthSettings(BaseModel):
    """Represents authentication configuration for a server."""

    api_key: str | None = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class MCPRootSettings(BaseModel):
    """Represents a root directory configuration for an MCP server."""

    uri: str
    """The URI identifying the root. Must start with file://"""

    name: Optional[str] = None
    """Optional name for the root."""

    server_uri_alias: Optional[str] = None
    """Optional URI alias for presentation to the server"""

    @field_validator("uri", "server_uri_alias")
    @classmethod
    def validate_uri(cls, v: str) -> str:
        """Validate that the URI starts with file:// (required by specification 2024-11-05)"""
        if not v.startswith("file://"):
            raise ValueError("Root URI must start with file://")
        return v

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class MCPServerSettings(BaseModel):
    """
    Represents the configuration for an individual server.
    """

    # TODO: saqadri - server name should be something a server can provide itself during initialization
    name: str | None = None
    """The name of the server."""

    # TODO: saqadri - server description should be something a server can provide itself during initialization
    description: str | None = None
    """The description of the server."""

    transport: Literal["stdio", "sse", "streamable_http", "websocket"] = "stdio"
    """The transport mechanism."""

    command: str | None = None
    """The command to execute the server (e.g. npx) in stdio mode."""

    args: List[str] = Field(default_factory=list)
    """The arguments for the server command in stdio mode."""

    url: str | None = None
    """The URL for the server for SSE, Streamble HTTP or websocket transport."""

    headers: Dict[str, str] | None = None
    """HTTP headers for SSE or Streamable HTTP requests."""

    http_timeout_seconds: int | None = None
    """
    HTTP request timeout in seconds for SSE or Streamable HTTP requests.

    Note: This is different from read_timeout_seconds, which 
    determines how long (in seconds) the client will wait for a new
    event before disconnecting
    """

    read_timeout_seconds: int | None = None
    """
    Timeout in seconds the client will wait for a new event before
    disconnecting from an SSE or Streamable HTTP server connection.
    """

    terminate_on_close: bool = True
    """
    For Streamable HTTP transport, whether to terminate the session on connection close.
    """

    auth: MCPServerAuthSettings | None = None
    """The authentication configuration for the server."""

    roots: List[MCPRootSettings] | None = None
    """Root directories this server has access to."""

    env: Dict[str, str] | None = None
    """Environment variables to pass to the server process."""

    allowed_tools: Set[str] | None = None
    """
    Set of tool names to allow from this server. If specified, only these tools will be exposed to agents. 
    Tool names should match exactly. 
    Note: Empty list will result in the agent having no access to tools.
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class MCPSettings(BaseModel):
    """Configuration for all MCP servers."""

    servers: Dict[str, MCPServerSettings] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @field_validator("servers", mode="before")
    def none_to_dict(cls, v):
        return {} if v is None else v


class VertexAIMixin(BaseModel):
    """Common fields for Vertex AI-compatible settings."""

    project: str | None = Field(
        default=None,
        validation_alias=AliasChoices("project", "PROJECT_ID", "GOOGLE_CLOUD_PROJECT"),
    )

    location: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "location", "LOCATION", "CLOUD_LOCATION", "GOOGLE_CLOUD_LOCATION"
        ),
    )

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class BedrockMixin(BaseModel):
    """Common fields for Bedrock-compatible settings."""

    aws_access_key_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("aws_access_key_id", "AWS_ACCESS_KEY_ID"),
    )

    aws_secret_access_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("aws_secret_access_key", "AWS_SECRET_ACCESS_KEY"),
    )

    aws_session_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("aws_session_token", "AWS_SESSION_TOKEN"),
    )

    aws_region: str | None = Field(
        default=None,
        validation_alias=AliasChoices("aws_region", "AWS_REGION"),
    )

    profile: str | None = Field(
        default=None,
        validation_alias=AliasChoices("profile", "AWS_PROFILE"),
    )

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class BedrockSettings(BaseSettings, BedrockMixin):
    """
    Settings for using Bedrock models in the MCP Agent application.
    """

    model_config = SettingsConfigDict(
        env_prefix="",
        extra="allow",
        arbitrary_types_allowed=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class AnthropicSettings(BaseSettings, VertexAIMixin, BedrockMixin):
    """
    Settings for using Anthropic models in the MCP Agent application.
    """

    api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "api_key", "ANTHROPIC_API_KEY", "anthropic__api_key"
        ),
    )
    default_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "default_model", "ANTHROPIC_DEFAULT_MODEL", "anthropic__default_model"
        ),
    )
    provider: Literal["anthropic", "bedrock", "vertexai"] = Field(
        default="anthropic",
        validation_alias=AliasChoices(
            "provider", "ANTHROPIC_PROVIDER", "anthropic__provider"
        ),
    )
    base_url: str | URL | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_prefix="ANTHROPIC_",
        extra="allow",
        arbitrary_types_allowed=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class CohereSettings(BaseSettings):
    """
    Settings for using Cohere models in the MCP Agent application.
    """

    api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("api_key", "COHERE_API_KEY", "cohere__api_key"),
    )

    model_config = SettingsConfigDict(
        env_prefix="COHERE_",
        extra="allow",
        arbitrary_types_allowed=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class OpenAISettings(BaseSettings):
    """
    Settings for using OpenAI models in the MCP Agent application.
    """

    api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("api_key", "OPENAI_API_KEY", "openai__api_key"),
    )

    reasoning_effort: Literal["low", "medium", "high"] = Field(
        default="medium",
        validation_alias=AliasChoices(
            "reasoning_effort", "OPENAI_REASONING_EFFORT", "openai__reasoning_effort"
        ),
    )
    base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "base_url", "OPENAI_BASE_URL", "openai__base_url"
        ),
    )

    user: str | None = Field(
        default=None,
        validation_alias=AliasChoices("user", "openai__user"),
    )

    default_headers: Dict[str, str] | None = None
    default_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "default_model", "OPENAI_DEFAULT_MODEL", "openai__default_model"
        ),
    )

    # NOTE: An http_client can be programmatically specified
    # and will be used by the OpenAI client. However, since it is
    # not a JSON-serializable object, it cannot be set via configuration.
    # http_client: Client | None = None

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        extra="allow",
        arbitrary_types_allowed=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class AzureSettings(BaseSettings):
    """
    Settings for using Azure models in the MCP Agent application.
    """

    api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "api_key", "AZURE_OPENAI_API_KEY", "AZURE_AI_API_KEY", "azure__api_key"
        ),
    )

    endpoint: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "endpoint", "AZURE_OPENAI_ENDPOINT", "AZURE_AI_ENDPOINT", "azure__endpoint"
        ),
    )

    api_version: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "api_version",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_AI_API_VERSION",
            "azure__api_version",
        ),
    )
    """API version for AzureOpenAI client (e.g., '2025-04-01-preview')"""

    azure_deployment: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "azure_deployment",
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_AI_DEPLOYMENT",
            "azure__azure_deployment",
        ),
    )
    """Azure deployment name (optional, defaults to model name if not specified)"""

    azure_ad_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "azure_ad_token",
            "AZURE_AD_TOKEN",
            "AZURE_AI_AD_TOKEN",
            "azure__azure_ad_token",
        ),
    )
    """Azure AD token for Entra ID authentication"""

    azure_ad_token_provider: Any | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "azure_ad_token_provider",
            "AZURE_AD_TOKEN_PROVIDER",
            "AZURE_AI_AD_TOKEN_PROVIDER",
        ),
    )
    """Azure AD token provider for dynamic token generation"""

    credential_scopes: List[str] | None = Field(
        default=["https://cognitiveservices.azure.com/.default"]
    )

    default_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "default_model", "AZURE_OPENAI_DEFAULT_MODEL", "azure__default_model"
        ),
    )

    model_config = SettingsConfigDict(
        env_prefix="AZURE_",
        extra="allow",
        arbitrary_types_allowed=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class GoogleSettings(BaseSettings, VertexAIMixin):
    """
    Settings for using Google models in the MCP Agent application.
    """

    api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "api_key", "GOOGLE_API_KEY", "GEMINI_API_KEY", "google__api_key"
        ),
    )

    vertexai: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "vertexai", "GOOGLE_VERTEXAI", "google__vertexai"
        ),
    )

    default_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "default_model", "GOOGLE_DEFAULT_MODEL", "google__default_model"
        ),
    )

    model_config = SettingsConfigDict(
        env_prefix="GOOGLE_",
        extra="allow",
        arbitrary_types_allowed=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class VertexAISettings(BaseSettings, VertexAIMixin):
    """Standalone Vertex AI settings (for future use)."""

    model_config = SettingsConfigDict(
        env_prefix="VERTEXAI_",
        extra="allow",
        arbitrary_types_allowed=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


class SubagentSettings(BaseModel):
    """
    Settings for discovering and loading project/user subagents (AgentSpec files).
    Supports common formats like Claude Code subagents.
    """

    enabled: bool = True
    """Enable automatic subagent discovery and loading."""

    search_paths: List[str] = Field(
        default_factory=lambda: [
            ".claude/agents",
            "~/.claude/agents",
            ".mcp-agent/agents",
            "~/.mcp-agent/agents",
        ]
    )
    """Ordered list of directories to scan. Earlier entries take precedence on name conflicts (project before user)."""

    pattern: str = "**/*.*"
    """Glob pattern within each directory to match files (YAML/JSON/Markdown supported)."""

    definitions: List[AgentSpec] = Field(default_factory=list)
    """Inline AgentSpec definitions directly in config."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class TemporalSettings(BaseModel):
    """
    Temporal settings for the MCP Agent application.
    """

    host: str
    namespace: str = "default"
    api_key: str | None = None
    tls: bool = False
    task_queue: str
    max_concurrent_activities: int | None = None
    timeout_seconds: int | None = 60
    rpc_metadata: Dict[str, str] | None = None
    id_reuse_policy: Literal[
        "allow_duplicate",
        "allow_duplicate_failed_only",
        "reject_duplicate",
        "terminate_if_running",
    ] = "allow_duplicate"

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class UsageTelemetrySettings(BaseModel):
    """
    Settings for usage telemetry in the MCP Agent application.
    Anonymized usage metrics are sent to a telemetry server to help improve the product.
    """

    enabled: bool = True
    """Enable usage telemetry in the MCP Agent application."""

    enable_detailed_telemetry: bool = False
    """If enabled, detailed telemetry data, including prompts and agents, will be sent to the telemetry server."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class TracePathSettings(BaseModel):
    """
    Settings for configuring trace file paths with dynamic elements like timestamps or session IDs.
    """

    path_pattern: str = "traces/mcp-agent-trace-{unique_id}.jsonl"
    """
    Path pattern for trace files with a {unique_id} placeholder.
    The placeholder will be replaced according to the unique_id setting.
    Example: "traces/mcp-agent-trace-{unique_id}.jsonl"
    """

    unique_id: Literal["timestamp", "session_id"] = "timestamp"
    """
    Type of unique identifier to use in the trace filename:
    """

    timestamp_format: str = "%Y%m%d_%H%M%S"
    """
    Format string for timestamps when unique_id is set to "timestamp".
    Uses Python's datetime.strftime format.
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class TraceOTLPSettings(BaseModel):
    """
    Settings for OTLP exporter in OpenTelemetry.
    """

    endpoint: str
    """OTLP endpoint for exporting traces."""

    headers: Dict[str, str] | None = None
    """Optional headers for OTLP exporter."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class OpenTelemetryExporterBase(BaseModel):
    """
    Base class for OpenTelemetry exporter configuration.

    This is used as the discriminated base for exporter-specific configs.
    """

    type: Literal["console", "file", "otlp"]

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class ConsoleExporterSettings(OpenTelemetryExporterBase):
    type: Literal["console"] = "console"


class FileExporterSettings(OpenTelemetryExporterBase):
    type: Literal["file"] = "file"
    path: str | None = None
    path_settings: TracePathSettings | None = None


class OTLPExporterSettings(OpenTelemetryExporterBase):
    type: Literal["otlp"] = "otlp"
    endpoint: str | None = None
    headers: Dict[str, str] | None = None


OpenTelemetryExporterSettings = Annotated[
    Union[
        ConsoleExporterSettings,
        FileExporterSettings,
        OTLPExporterSettings,
    ],
    Field(discriminator="type"),
]


class OpenTelemetrySettings(BaseModel):
    """
    OTEL settings for the MCP Agent application.
    """

    enabled: bool = False

    exporters: List[
        Union[Literal["console", "file", "otlp"], OpenTelemetryExporterSettings]
    ] = []
    """
    Exporters to use (can enable multiple simultaneously). Each exporter has
    its own typed configuration.

    Backward compatible: a YAML list of literal strings (e.g. ["console", "otlp"]) is
    accepted and will be transformed, sourcing settings from legacy fields
    like `otlp_settings`, `path` and `path_settings` if present.
    """

    service_name: str = "mcp-agent"
    service_instance_id: str | None = None
    service_version: str | None = None

    sample_rate: float = 1.0
    """Sample rate for tracing (1.0 = sample everything)"""

    # Deprecated: use exporters: [{ type: "otlp", ... }]
    otlp_settings: TraceOTLPSettings | None = None
    """Deprecated single OTLP settings. Prefer exporters list with type "otlp"."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @model_validator(mode="before")
    @classmethod
    def _coerce_exporters_schema(cls, data: Dict) -> Dict:
        """
        Backward compatibility shim to allow:
          - exporters: ["console", "file", "otlp"] with legacy per-exporter fields
          - exporters already in discriminated-union form
        """
        if not isinstance(data, dict):
            return data

        exporters = data.get("exporters")

        # If exporters are already objects with a 'type', leave as-is
        if isinstance(exporters, list) and all(
            isinstance(e, dict) and "type" in e for e in exporters
        ):
            return data

        # If exporters are literal strings, up-convert to typed configs
        if isinstance(exporters, list) and all(isinstance(e, str) for e in exporters):
            typed_exporters: List[Dict] = []

            # Legacy helpers (can arrive as dicts or BaseModel instances)
            legacy_otlp = data.get("otlp_settings")
            if isinstance(legacy_otlp, BaseModel):
                legacy_otlp = legacy_otlp.model_dump(exclude_none=True)
            elif not isinstance(legacy_otlp, dict):
                legacy_otlp = {}

            legacy_path = data.get("path")
            legacy_path_settings = data.get("path_settings")
            if isinstance(legacy_path_settings, BaseModel):
                legacy_path_settings = legacy_path_settings.model_dump(
                    exclude_none=True
                )

            for name in exporters:
                if name == "console":
                    typed_exporters.append({"type": "console"})
                elif name == "file":
                    typed_exporters.append(
                        {
                            "type": "file",
                            "path": legacy_path,
                            "path_settings": legacy_path_settings,
                        }
                    )
                elif name == "otlp":
                    typed_exporters.append(
                        {
                            "type": "otlp",
                            "endpoint": (legacy_otlp or {}).get("endpoint"),
                            "headers": (legacy_otlp or {}).get("headers"),
                        }
                    )
                else:
                    raise ValueError(
                        f"Unsupported OpenTelemetry exporter '{name}'. "
                        "Supported exporters: console, file, otlp."
                    )

            # Overwrite with transformed list
            data["exporters"] = typed_exporters

        return data

    @model_validator(mode="after")
    @classmethod
    def _finalize_exporters(cls, values: "OpenTelemetrySettings"):
        """Ensure exporters are instantiated as typed configs even if literals were provided."""

        typed_exporters: List[OpenTelemetryExporterSettings] = []

        legacy_path = getattr(values, "path", None)
        legacy_path_settings = getattr(values, "path_settings", None)
        if isinstance(legacy_path_settings, dict):
            legacy_path_settings = TracePathSettings.model_validate(
                legacy_path_settings
            )

        for exporter in values.exporters:
            if isinstance(exporter, OpenTelemetryExporterBase):
                typed_exporters.append(exporter)  # Already typed
                continue

            if exporter == "console":
                typed_exporters.append(ConsoleExporterSettings())
            elif exporter == "file":
                typed_exporters.append(
                    FileExporterSettings(
                        path=legacy_path,
                        path_settings=legacy_path_settings,
                    )
                )
            elif exporter == "otlp":
                endpoint = None
                headers = None
                if values.otlp_settings:
                    endpoint = getattr(values.otlp_settings, "endpoint", None)
                    headers = getattr(values.otlp_settings, "headers", None)
                typed_exporters.append(
                    OTLPExporterSettings(endpoint=endpoint, headers=headers)
                )
            else:  # pragma: no cover - safeguarded by pre-validator, but keep defensive path
                raise ValueError(
                    f"Unsupported OpenTelemetry exporter '{exporter}'. "
                    "Supported exporters: console, file, otlp."
                )

        values.exporters = typed_exporters

        # Remove legacy extras once we've consumed them to avoid leaking into dumps
        if hasattr(values, "path"):
            delattr(values, "path")
        if hasattr(values, "path_settings"):
            delattr(values, "path_settings")

        return values


class LogPathSettings(BaseModel):
    """
    Settings for configuring log file paths with dynamic elements like timestamps or session IDs.
    """

    path_pattern: str = "logs/mcp-agent-{unique_id}.jsonl"
    """
    Path pattern for log files with a {unique_id} placeholder.
    The placeholder will be replaced according to the unique_id setting.
    Example: "logs/mcp-agent-{unique_id}.jsonl"
    """

    unique_id: Literal["timestamp", "session_id"] = "timestamp"
    """
    Type of unique identifier to use in the log filename:
    - timestamp: Uses the current time formatted according to timestamp_format
    - session_id: Generates a UUID for the session
    """

    timestamp_format: str = "%Y%m%d_%H%M%S"
    """
    Format string for timestamps when unique_id is set to "timestamp".
    Uses Python's datetime.strftime format.
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class LoggerSettings(BaseModel):
    """
    Logger settings for the MCP Agent application.
    """

    # Original transport configuration (kept for backward compatibility)
    type: Literal["none", "console", "file", "http"] = "console"

    transports: List[Literal["none", "console", "file", "http"]] = []
    """List of transports to use (can enable multiple simultaneously)"""

    level: Literal["debug", "info", "warning", "error"] = "info"
    """Minimum logging level"""

    progress_display: bool = False
    """Enable or disable the progress display"""

    path: str = "mcp-agent.jsonl"
    """Path to log file, if logger 'type' is 'file'."""

    # Settings for advanced log path configuration
    path_settings: LogPathSettings | None = None
    """
    Save log files with more advanced path semantics, like having timestamps or session id in the log name.
    """

    batch_size: int = 100
    """Number of events to accumulate before processing"""

    flush_interval: float = 2.0
    """How often to flush events in seconds"""

    max_queue_size: int = 2048
    """Maximum queue size for event processing"""

    # HTTP transport settings
    http_endpoint: str | None = None
    """HTTP endpoint for event transport"""

    http_headers: dict[str, str] | None = None
    """HTTP headers for event transport"""

    http_timeout: float = 5.0
    """HTTP timeout seconds for event transport"""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class Settings(BaseSettings):
    """
    Settings class for the MCP Agent application.
    """

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        nested_model_default_partial_update=True,
    )  # Customize the behavior of settings here

    name: str | None = None
    """The name of the MCP application"""

    description: str | None = None
    """The description of the MCP application"""

    mcp: MCPSettings | None = Field(default_factory=MCPSettings)
    """MCP config, such as MCP servers"""

    execution_engine: Literal["asyncio", "temporal"] = "asyncio"
    """Execution engine for the MCP Agent application"""

    temporal: TemporalSettings | None = None
    """Settings for Temporal workflow orchestration"""

    anthropic: AnthropicSettings | None = Field(default_factory=AnthropicSettings)
    """Settings for using Anthropic models in the MCP Agent application"""

    bedrock: BedrockSettings | None = Field(default_factory=BedrockSettings)
    """Settings for using Bedrock models in the MCP Agent application"""

    cohere: CohereSettings | None = Field(default_factory=CohereSettings)
    """Settings for using Cohere models in the MCP Agent application"""

    openai: OpenAISettings | None = Field(default_factory=OpenAISettings)
    """Settings for using OpenAI models in the MCP Agent application"""

    azure: AzureSettings | None = Field(default_factory=AzureSettings)
    """Settings for using Azure models in the MCP Agent application"""

    google: GoogleSettings | None = Field(default_factory=GoogleSettings)
    """Settings for using Google models in the MCP Agent application"""

    otel: OpenTelemetrySettings | None = OpenTelemetrySettings()
    """OpenTelemetry logging settings for the MCP Agent application"""

    logger: LoggerSettings | None = LoggerSettings()
    """Logger settings for the MCP Agent application"""

    usage_telemetry: UsageTelemetrySettings | None = UsageTelemetrySettings()
    """Usage tracking settings for the MCP Agent application"""

    agents: SubagentSettings | None = SubagentSettings()
    """Settings for defining and loading subagents for the MCP Agent application"""

    def __eq__(self, other):  # type: ignore[override]
        if not isinstance(other, Settings):
            return NotImplemented
        # Compare by full JSON dump to avoid differences in internal field-set tracking
        return self.model_dump(mode="json") == other.model_dump(mode="json")

    @classmethod
    def find_config(cls) -> Path | None:
        """Find the config file in the current directory or parent directories."""
        return cls._find_config(["mcp-agent.config.yaml", "mcp_agent.config.yaml"])

    @classmethod
    def find_secrets(cls) -> Path | None:
        """Find the secrets file in the current directory or parent directories."""
        return cls._find_config(["mcp-agent.secrets.yaml", "mcp_agent.secrets.yaml"])

    @classmethod
    def _find_config(cls, filenames: List[str]) -> Path | None:
        """Find a file by name in current, parents, and `.mcp-agent` subdirs, with home fallback.

        Search order:
          - For each directory from CWD -> root:
              - <dir>/<filename>
              - <dir>/.mcp-agent/<filename>
          - Home-level fallback:
              - ~/.mcp-agent/<filename>
        Returns the first match found.
        """
        current_dir = Path.cwd()

        # Check current directory and parent directories (direct and .mcp-agent subdir)
        while True:
            for filename in filenames:
                direct = current_dir / filename
                if direct.exists():
                    return direct

                mcp_dir = current_dir / ".mcp-agent" / filename
                if mcp_dir.exists():
                    return mcp_dir

            if current_dir == current_dir.parent:
                break
            current_dir = current_dir.parent

        # Home directory fallback
        try:
            home = Path.home()
            for filename in filenames:
                home_file = home / ".mcp-agent" / filename
                if home_file.exists():
                    return home_file
        except Exception:
            pass

        return None


class PreloadSettings(BaseSettings):
    """
    Class for preloaded settings of the MCP Agent application.
    """

    model_config = SettingsConfigDict(env_prefix="mcp_app_settings_")

    preload: str | None = None
    """ A literal YAML string to interpret as a serialized Settings model.
    For example, the value given by `pydantic_yaml.to_yaml_str(settings)`.
    Env Var: `MCP_APP_SETTINGS_PRELOAD`.
    """

    preload_strict: bool = False
    """ Whether to perform strict parsing of the preload string.
    If true, failures in parsing will raise an exception.
    If false (default), failures in parsing will fall through to the default
    settings loading.
    Env Var: `MCP_APP_SETTINGS_PRELOAD_STRICT`.
    """


# Global settings object
_settings: Settings | None = None


def _clear_global_settings():
    """
    Convenience for testing - clear the global memoized settings.
    """
    global _settings
    _settings = None


def _set_and_warn_global_settings(settings: Settings) -> None:
    """Set global settings and warn if called from non-main thread."""
    global _settings
    _settings = settings
    # Thread-safety advisory: warn when setting global singleton from non-main thread
    if threading.current_thread() is not threading.main_thread():
        warnings.warn(
            "get_settings() is setting the global Settings singleton from a non-main thread. "
            "In multithreaded environments, use get_settings(set_global=False) to avoid "
            "global state modification, or pass the Settings instance explicitly to MCPApp(settings=...).",
            stacklevel=3,  # Adjusted stacklevel since we're now in a helper function
        )


def _check_file_exists(file_path: (str | Path)) -> bool:
    """Check if a file exists at the given path."""
    return Path(file_path).exists()


def _read_file_content(file_path: (str | Path)) -> str:
    """Read and return the contents of a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _load_yaml_from_string(yaml_content: str) -> dict:
    """Load YAML content from a string."""
    return yaml.safe_load(yaml_content) or {}


def get_settings(config_path: str | None = None, set_global: bool = True) -> Settings:
    """Get settings instance, automatically loading from config file if available.

    Args:
        config_path: Optional path to config file. If None, searches for config automatically.
        set_global: Whether to set the loaded settings as the global singleton. Default is True for backward
                    compatibility. Set to False for multi-threaded environments to avoid global state modification.

    Returns:
        Settings instance with loaded configuration.
    """

    def deep_merge(base: dict, update: dict) -> dict:
        """Recursively merge two dictionaries, preserving nested structures."""
        merged = base.copy()
        for key, value in update.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    # Only return cached global settings if we're in set_global mode
    if set_global:
        global _settings
        if _settings:
            return _settings

    merged_settings = {}

    preload_settings = PreloadSettings()
    preload_config = preload_settings.preload
    if preload_config:
        try:
            # Write to an intermediate buffer to force interpretation as literal data and not a file path
            buf = StringIO()
            buf.write(preload_config)
            buf.seek(0)
            yaml_settings = yaml.safe_load(buf) or {}

            # Preload is authoritative: construct from YAML directly (no env overlay)
            return Settings(**yaml_settings)
        except Exception as e:
            if preload_settings.preload_strict:
                raise ValueError(
                    "MCP App Preloaded Settings value failed validation"
                ) from e
            # TODO: Decide the right logging call here - I'm cautious that it's in a very central scope
            print(
                f"MCP App Preloaded Settings value failed validation: {e}",
                file=sys.stderr,
            )

    # Determine the config file to use
    if config_path:
        config_file = Path(config_path)
        if not _check_file_exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_path}")
    else:
        config_file = Settings.find_config()

    # If we found a config file, load it
    if config_file and _check_file_exists(config_file):
        file_content = _read_file_content(config_file)
        yaml_settings = _load_yaml_from_string(file_content)
        merged_settings = yaml_settings

        # Try to find secrets in the same directory as the config file
        config_dir = config_file.parent
        secrets_found = False
        for secrets_filename in ["mcp-agent.secrets.yaml", "mcp_agent.secrets.yaml"]:
            secrets_file = config_dir / secrets_filename
            if _check_file_exists(secrets_file):
                secrets_content = _read_file_content(secrets_file)
                yaml_secrets = _load_yaml_from_string(secrets_content)
                merged_settings = deep_merge(merged_settings, yaml_secrets)
                secrets_found = True
                break

        # If no secrets were found in the config directory, fall back to discovery
        if not secrets_found:
            secrets_file = Settings.find_secrets()
            if secrets_file and _check_file_exists(secrets_file):
                secrets_content = _read_file_content(secrets_file)
                yaml_secrets = _load_yaml_from_string(secrets_content)
                merged_settings = deep_merge(merged_settings, yaml_secrets)

        settings = Settings(**merged_settings)
        if set_global:
            _set_and_warn_global_settings(settings)
        return settings

    # No valid config found anywhere
    settings = Settings()
    if set_global:
        _set_and_warn_global_settings(settings)
    return settings
