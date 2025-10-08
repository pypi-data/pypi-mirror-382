"""
Common constants for EGRC Platform.

This module contains constants that are shared across all EGRC services
and microservices in the platform.
"""

from enum import Enum


class Environment(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class HTTPStatus:
    """HTTP status codes."""

    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


class DatabaseConstants:
    """Database-related constants."""

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    DEFAULT_ORDER_BY = "created_at"
    DEFAULT_ORDER_DIRECTION = "desc"

    # Connection pool settings
    DEFAULT_POOL_SIZE = 5
    DEFAULT_MAX_OVERFLOW = 10
    DEFAULT_POOL_TIMEOUT = 30
    DEFAULT_POOL_RECYCLE = 3600
    DEFAULT_POOL_PRE_PING = True
    DEFAULT_QUERY_TIMEOUT = 30
    DEFAULT_CONNECTION_TIMEOUT = 10

    # Migration settings
    MIGRATION_DIR = "alembic"
    MIGRATION_SCRIPT_LOCATION = "alembic"


class SecurityConstants:
    """Security-related constants."""

    # JWT settings
    JWT_ALGORITHM = "HS256"
    DEFAULT_JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 7

    # Password settings
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL_CHARS = True

    # Encryption settings
    DEFAULT_ENCRYPTION_ALGORITHM = "AES-256-GCM"
    DEFAULT_KEY_DERIVATION_ITERATIONS = 100000

    # Rate limiting
    DEFAULT_RATE_LIMIT = 100  # requests per minute
    DEFAULT_RATE_LIMIT_REQUESTS = 100
    DEFAULT_RATE_LIMIT_WINDOW = 60  # seconds
    DEFAULT_RATE_LIMIT_BURST = 10
    AUTH_RATE_LIMIT = 5  # login attempts per minute

    # CORS settings
    DEFAULT_CORS_ORIGINS = ["*"]
    DEFAULT_CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    DEFAULT_CORS_HEADERS = ["*"]
    DEFAULT_CORS_CREDENTIALS = True

    # Session settings
    SESSION_TIMEOUT_MINUTES = 30
    MAX_CONCURRENT_SESSIONS = 5


class AppConstants:
    """Application-related constants."""

    APP_NAME = "EGRC Core"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = (
        "EGRC Core - Shared functionality for Enterprise Governance, "
        "Risk, and Compliance platform"
    )
    APP_AUTHOR = "EGRC Team"
    APP_EMAIL = "team@egrc.com"
    APP_URL = "https://github.com/egrc/egrc-core"
    APP_LICENSE = "MIT"


class EnvironmentConstants:
    """Environment-related constants."""

    DEFAULT_ENVIRONMENT = "development"
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"
    ENV_PRODUCTION = "production"
    ENV_DEVELOPMENT = "development"
    ENV_TESTING = "testing"
    ENV_STAGING = "staging"
    ENV_LOCAL = "local"

    # Environment-specific settings
    ENVIRONMENT_SETTINGS = {
        "production": {
            "debug": False,
            "log_level": "WARNING",
            "database_pool_size": 20,
        },
        "staging": {
            "debug": False,
            "log_level": "INFO",
            "database_pool_size": 10,
        },
        "development": {
            "debug": True,
            "log_level": "DEBUG",
            "database_pool_size": 5,
        },
        "testing": {
            "debug": True,
            "log_level": "DEBUG",
            "database_pool_size": 1,
        },
        "local": {
            "debug": True,
            "log_level": "DEBUG",
            "database_pool_size": 2,
        },
    }


class LoggingConstants:
    """Logging-related constants."""

    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_LOG_FORMAT = "text"
    DEFAULT_LOG_FILE = "egrc.log"
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    DEFAULT_LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT = 5
    DEFAULT_LOG_FILE_BACKUP_COUNT = 5
    DEFAULT_LOG_FILE_ROTATION = "daily"

    # Log levels
    LOG_LEVEL_DEBUG = "DEBUG"
    LOG_LEVEL_INFO = "INFO"
    LOG_LEVEL_WARNING = "WARNING"
    LOG_LEVEL_ERROR = "ERROR"
    LOG_LEVEL_CRITICAL = "CRITICAL"

    # Log formats
    LOG_FORMAT_JSON = "json"
    LOG_FORMAT_TEXT = "text"
    LOG_FORMAT_COLORED = "colored"


class AuditConstants:
    """Audit-related constants."""

    # Audit actions
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"

    # Audit statuses
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"

    # Audit categories
    SECURITY = "SECURITY"
    BUSINESS = "BUSINESS"
    SYSTEM = "SYSTEM"
    DATA = "DATA"


class GraphQLConstants:
    """GraphQL-related constants."""

    MAX_QUERY_DEPTH = 10
    MAX_QUERY_COMPLEXITY = 1000
    MAX_QUERY_COST = 1000
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class CacheConstants:
    """Cache-related constants."""

    REDIS = "redis"
    DEFAULT_TTL = 300  # 5 minutes
    USER_CACHE_TTL = 1800  # 30 minutes
    SESSION_CACHE_TTL = 1800  # 30 minutes
    PERMISSION_CACHE_TTL = 3600  # 1 hour
    CONFIG_CACHE_TTL = 7200  # 2 hours

    # Redis connection settings
    DEFAULT_REDIS_POOL_SIZE = 20
    DEFAULT_REDIS_MAX_CONNECTIONS = 20
    DEFAULT_REDIS_RETRY_ON_TIMEOUT = True
    DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT = 5
    DEFAULT_REDIS_SOCKET_TIMEOUT = 5
    DEFAULT_REDIS_HEALTH_CHECK_INTERVAL = 30

    # Cache key settings
    CACHE_KEY_PREFIX = "egrc"
    DEFAULT_CACHE_TYPE = "redis"


class FileConstants:
    """File-related constants."""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gi", "image/webp"]
    ALLOWED_DOCUMENT_TYPES = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/csv",
    ]

    # File upload paths
    UPLOAD_PATH = "/uploads"
    TEMP_PATH = "/tmp"
    BACKUP_PATH = "/backups"


class EmailConstants:
    """Email-related constants."""

    DEFAULT_FROM_EMAIL = "noreply@egrc.com"
    DEFAULT_FROM_NAME = "EGRC Platform"
    MAX_RECIPIENTS = 100
    EMAIL_QUEUE_NAME = "email_queue"

    # Email templates
    WELCOME_TEMPLATE = "welcome"
    PASSWORD_RESET_TEMPLATE = "password_reset"
    ACCOUNT_ACTIVATION_TEMPLATE = "account_activation"
    NOTIFICATION_TEMPLATE = "notification"


class NotificationConstants:
    """Notification-related constants."""

    # Notification types
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

    # Notification channels
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

    # Notification priorities
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class WorkflowConstants:
    """Workflow-related constants."""

    # Workflow statuses
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    # Workflow actions
    SUBMIT = "submit"
    APPROVE = "approve"
    REJECT = "reject"
    ASSIGN = "assign"
    COMPLETE = "complete"
    CANCEL = "cancel"


class ComplianceConstants:
    """Compliance-related constants."""

    # Compliance frameworks
    SOX = "sox"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"

    # Compliance statuses
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_ASSESSED = "not_assessed"

    # Risk levels
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class APIResponseMessages:
    """Standard API response messages."""

    SUCCESS = "Operation completed successfully"
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    NOT_FOUND = "Resource not found"
    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "Access denied"
    VALIDATION_ERROR = "Validation failed"
    INTERNAL_ERROR = "Internal server error"
    RATE_LIMITED = "Rate limit exceeded"


class ErrorCodes:
    """Standard error codes."""

    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"

    # Authentication errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"

    # Database errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_CONSTRAINT_ERROR = "DATABASE_CONSTRAINT_ERROR"

    # External service errors
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"
    EXTERNAL_SERVICE_TIMEOUT = "EXTERNAL_SERVICE_TIMEOUT"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


class DefaultValues:
    """Default values for various configurations."""

    # Pagination
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20

    # Sorting
    DEFAULT_SORT_FIELD = "created_at"
    DEFAULT_SORT_ORDER = "desc"

    # Timeouts
    DEFAULT_REQUEST_TIMEOUT = 30
    DEFAULT_DATABASE_TIMEOUT = 30
    DEFAULT_CACHE_TIMEOUT = 300

    # Limits
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BATCH_SIZE = 100
    DEFAULT_CONCURRENT_REQUESTS = 10


class RegexPatterns:
    """Common regex patterns."""

    EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    PHONE = r"^\+?1?\d{9,15}$"
    UUID = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    ALPHANUMERIC = r"^[a-zA-Z0-9]+$"
    ALPHANUMERIC_WITH_SPACES = r"^[a-zA-Z0-9\s]+$"
    ALPHANUMERIC_WITH_UNDERSCORES = r"^[a-zA-Z0-9_]+$"
    STRONG_PASSWORD = (
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )


class DateFormats:
    """Common date formats."""

    ISO_DATE = "%Y-%m-%d"
    ISO_DATETIME = "%Y-%m-%dT%H:%M:%S"
    ISO_DATETIME_WITH_TZ = "%Y-%m-%dT%H:%M:%S%z"
    DISPLAY_DATE = "%B %d, %Y"
    DISPLAY_DATETIME = "%B %d, %Y at %I:%M %p"
    FILENAME_DATE = "%Y%m%d_%H%M%S"


class ContentTypes:
    """Common content types."""

    JSON = "application/json"
    XML = "application/xml"
    FORM_DATA = "multipart/form-data"
    URL_ENCODED = "application/x-www-form-urlencoded"
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"
    TEXT_CSV = "text/csv"
    APPLICATION_PDF = "application/pdf"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"


class Headers:
    """Common HTTP headers."""

    AUTHORIZATION = "Authorization"
    CONTENT_TYPE = "Content-Type"
    ACCEPT = "Accept"
    USER_AGENT = "User-Agent"
    X_REQUEST_ID = "X-Request-ID"
    X_CORRELATION_ID = "X-Correlation-ID"
    X_TENANT_ID = "X-Tenant-ID"
    X_USER_ID = "X-User-ID"
    X_API_KEY = "X-API-Key"
    X_FORWARDED_FOR = "X-Forwarded-For"
    X_REAL_IP = "X-Real-IP"


class QueueNames:
    """Queue names for background tasks."""

    EMAIL_QUEUE = "email_queue"
    AUDIT_QUEUE = "audit_queue"
    NOTIFICATION_QUEUE = "notification_queue"
    REPORT_QUEUE = "report_queue"
    BACKUP_QUEUE = "backup_queue"
    CLEANUP_QUEUE = "cleanup_queue"
    SYNC_QUEUE = "sync_queue"


class TaskPriorities:
    """Task priorities for background jobs."""

    LOW = 1
    NORMAL = 5
    HIGH = 10
    URGENT = 20


class RetryPolicies:
    """Retry policies for failed operations."""

    # Exponential backoff delays (in seconds)
    EXPONENTIAL_BACKOFF = [1, 2, 4, 8, 16, 32, 64]

    # Fixed delays (in seconds)
    FIXED_DELAY = [5, 10, 15, 30, 60]

    # Linear backoff delays (in seconds)
    LINEAR_BACKOFF = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


# Export all constants for easy importing
__all__ = [
    "Environment",
    "LogLevel",
    "HTTPStatus",
    "DatabaseConstants",
    "SecurityConstants",
    "AuditConstants",
    "GraphQLConstants",
    "CacheConstants",
    "FileConstants",
    "EmailConstants",
    "NotificationConstants",
    "WorkflowConstants",
    "ComplianceConstants",
    "APIResponseMessages",
    "ErrorCodes",
    "DefaultValues",
    "RegexPatterns",
    "DateFormats",
    "ContentTypes",
    "Headers",
    "QueueNames",
    "TaskPriorities",
    "RetryPolicies",
]
