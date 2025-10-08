"""
EGRC Core - Governance, Risk, and Compliance Platform.

This module provides the core functionality for the EGRC platform including
exceptions, database models, utilities, and comprehensive audit logging.
"""

# Core modules
from . import (
    audit,
    cache,
    config,
    core,
    database,
    graphql,
    http,
    llm,
    messaging,
    monitoring,
    security,
    storage,
    testing,
    utils,
)

# Version information
from .__version__ import (
    __author__,
    __description__,
    __email__,
    __license__,
    __url__,
    __version__,
    __version_info__,
)
from .audit import (
    AuditContext,
    AuditService,
    audit_hook,
    get_processor_stats,
    get_queue_status,
    log_application_event,
    log_audit,
    log_audit_event,
    log_business_event,
    log_security_event,
    register_model_for_audit,
    setup_audit_middleware,
    start_event_processor,
    stop_event_processor,
    submit_audit_event,
)
from .config import AppConstants, DatabaseConstants, SecurityConstants, Settings

# Re-export commonly used items from core modules
from .core import (
    AuthMiddleware,
    GlobalID,
    TenantMiddleware,
    decode_global_id,
    encode_global_id,
)
from .database import (
    Base,
    BaseCRUD,
    PaginatedResult,
    PaginationParams,
    get_async_db_session,
    get_db_session,
)

# Exception classes
from .exceptions.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    CacheException,
    ConfigurationError,
    ConflictError,
    DatabaseError,
    EGRCException,
    ExternalServiceError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .llm import (
    AnthropicProvider,
    ConversationService,
    DeepSeekProvider,
    LlamaProvider,
    LLMConversation,
    LLMRequest,
    LLMResponse,
    LLMService,
    OpenAIProvider,
    UsageService,
    get_conversation_service,
    get_llm_provider,
    get_llm_service,
    get_usage_service,
)
from .utils import (
    EnvironmentValidator,
    generate_api_key,
    generate_secure_token,
    generate_uuid,
    hash_password,
    validate_email,
    validate_password_strength,
    verify_password,
)


# Utils module is now properly implemented


__all__ = [
    # Version
    "__version__",
    "__version_info__",
    "__author__",
    "__email__",
    "__description__",
    "__url__",
    "__license__",
    # Core modules
    "core",
    "database",
    "config",
    "utils",
    "graphql",
    "audit",
    "cache",
    "llm",
    "messaging",
    "security",
    "monitoring",
    "storage",
    "http",
    "testing",
    # Exceptions
    "EGRCException",
    "ValidationError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "BusinessLogicError",
    "ExternalServiceError",
    "DatabaseError",
    "RateLimitError",
    "ConfigurationError",
    "CacheException",
    # Core functionality
    "AuthMiddleware",
    "TenantMiddleware",
    "GlobalID",
    "encode_global_id",
    "decode_global_id",
    # Database
    "Base",
    "get_db_session",
    "get_async_db_session",
    "BaseCRUD",
    "PaginationParams",
    "PaginatedResult",
    # Configuration
    "Settings",
    "AppConstants",
    "DatabaseConstants",
    "SecurityConstants",
    # Utils module is now properly implemented
    "EnvironmentValidator",
    "generate_api_key",
    "generate_secure_token",
    "generate_uuid",
    "hash_password",
    "validate_email",
    "validate_password_strength",
    "verify_password",
    # Audit system
    "AuditService",
    "audit_hook",
    "AuditContext",
    "log_audit",
    "log_audit_event",
    "setup_audit_middleware",
    "register_model_for_audit",
    "log_application_event",
    "log_business_event",
    "log_security_event",
    "start_event_processor",
    "stop_event_processor",
    "submit_audit_event",
    "get_processor_stats",
    "get_queue_status",
    # LLM Services
    "LLMService",
    "get_llm_service",
    "ConversationService",
    "get_conversation_service",
    "UsageService",
    "get_usage_service",
    # LLM Models
    "LLMRequest",
    "LLMResponse",
    "LLMConversation",
    # LLM Providers
    "OpenAIProvider",
    "DeepSeekProvider",
    "LlamaProvider",
    "AnthropicProvider",
    "get_llm_provider",
]
