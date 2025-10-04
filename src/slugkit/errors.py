"""
Error handling utilities for SlugKit SDK.
"""

import time
import json
from typing import Optional, Any
from enum import Enum
import httpx


class ErrorSeverity(Enum):
    """Error severity levels for categorization."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorContext:
    """Structured error context for better error reporting and debugging."""

    def __init__(
        self,
        operation: str,
        endpoint: Optional[str] = None,
        base_url: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs,
    ):
        self.operation = operation
        self.endpoint = endpoint
        self.base_url = base_url
        self.user_id = user_id
        self.timestamp = time.time()
        self.additional_data = kwargs

        # Store all kwargs as attributes for easy access
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "operation": self.operation,
            "endpoint": self.endpoint,
            "base_url": self.base_url,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "additional_data": self.additional_data,
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        parts = [f"Operation: {self.operation}"]
        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")
        if self.base_url:
            parts.append(f"Base URL: {self.base_url}")
        if self.user_id:
            parts.append(f"User ID: {self.user_id}")
        if self.additional_data:
            parts.append(f"Additional: {self.additional_data}")
        return " | ".join(parts)


class SlugKitError(Exception):
    """Base exception for all SlugKit errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
        timestamp: Optional[float] = None,
    ):
        super().__init__(message)
        self.message = message
        self.context = context or ErrorContext("unknown")
        self.cause = cause
        self.timestamp = timestamp or time.time()

    def add_context(self, **kwargs) -> "SlugKitError":
        """Add additional context information."""
        for key, value in kwargs.items():
            setattr(self.context, key, value)
        return self

    def get_context_info(self) -> str:
        """Get formatted context information."""
        return str(self.context)

    def __str__(self) -> str:
        """Enhanced string representation with context."""
        parts = [self.message]
        if self.context:
            parts.append(f"Context: {self.get_context_info()}")
        if self.cause:
            parts.append(f"Caused by: {str(self.cause)}")
        return " | ".join(parts)


class SlugKitConnectionError(SlugKitError):
    """Network connectivity or connection-related errors."""

    pass


class SlugKitAuthenticationError(SlugKitError):
    """Authentication and authorization errors."""

    pass


class SlugKitClientError(SlugKitError):
    """Client-side errors (bad requests, validation, etc.)."""

    pass


class SlugKitServerError(SlugKitError):
    """Server-side errors."""

    pass


class SlugKitRateLimitError(SlugKitError):
    """Rate limiting and throttling errors with retry information."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
        timestamp: Optional[float] = None,
        retry_after: Optional[int] = None,
        rate_limit_reason: Optional[str] = None,
        rpm_remaining: Optional[int] = None,
        daily_remaining: Optional[int] = None,
        monthly_remaining: Optional[int] = None,
        lifetime_remaining: Optional[int] = None,
    ):
        super().__init__(message, context, cause, timestamp)
        self.retry_after = retry_after
        self.rate_limit_reason = rate_limit_reason
        self.rpm_remaining = rpm_remaining
        self.daily_remaining = daily_remaining
        self.monthly_remaining = monthly_remaining
        self.lifetime_remaining = lifetime_remaining

    def __str__(self) -> str:
        """Enhanced string representation with rate limit details."""
        parts = [self.message]

        # Add rate limit reason if available
        if self.rate_limit_reason:
            parts.append(f"Reason: {self.rate_limit_reason}")

        # Add retry after information
        if self.retry_after is not None:
            hours = self.retry_after / 3600
            if hours >= 1:
                parts.append(f"Retry after: {self.retry_after} seconds ({hours:.1f} hours)")
            elif self.retry_after >= 60:
                minutes = self.retry_after / 60
                parts.append(f"Retry after: {self.retry_after} seconds ({minutes:.1f} minutes)")
            else:
                parts.append(f"Retry after: {self.retry_after} seconds")

        # Add quota information if available
        quota_parts = []
        if self.rpm_remaining is not None:
            quota_parts.append(f"RPM: {self.rpm_remaining}")
        if self.daily_remaining is not None:
            quota_parts.append(f"Daily: {self.daily_remaining}")
        if self.monthly_remaining is not None:
            quota_parts.append(f"Monthly: {self.monthly_remaining}")
        if self.lifetime_remaining is not None:
            quota_parts.append(f"Lifetime: {self.lifetime_remaining}")

        if quota_parts:
            parts.append(f"Remaining quotas: {', '.join(quota_parts)}")

        # Add context information
        if self.context:
            parts.append(f"Context: {self.get_context_info()}")

        # Add cause information
        if self.cause:
            parts.append(f"Caused by: {str(self.cause)}")

        return " | ".join(parts)


class SlugKitValidationError(SlugKitError):
    """Data validation and format errors."""

    pass


class SlugKitTimeoutError(SlugKitError):
    """Request timeout errors."""

    pass


class SlugKitQuotaError(SlugKitError):
    """Quota and usage limit errors."""

    pass


class SlugKitConfigurationError(SlugKitError):
    """Configuration and setup errors."""

    pass


def get_error_recovery_suggestions(error: SlugKitError) -> list[str]:
    """Get actionable recovery suggestions for an error."""
    suggestions = []

    if isinstance(error, SlugKitConnectionError):
        suggestions.extend(
            [
                "Verify the server URL is correct and accessible",
                "Check your internet connection",
                "Try again in a few moments (network issues are often temporary)",
                "Verify firewall/proxy settings if applicable",
            ]
        )

    elif isinstance(error, SlugKitAuthenticationError):
        suggestions.extend(
            [
                "Verify your API key is correct and not expired",
                "Check that your API key has the required permissions",
                "Ensure the API key is properly formatted",
                "Contact support if the issue persists",
            ]
        )

    elif isinstance(error, SlugKitClientError):
        suggestions.extend(
            [
                "Review the request parameters and format",
                "Check the API documentation for correct usage",
                "Verify all required fields are provided",
                "Ensure data types match expected formats",
            ]
        )

    elif isinstance(error, SlugKitValidationError):
        suggestions.extend(
            [
                "Review the input data for format issues",
                "Check that all required fields are present",
                "Verify data types and constraints",
                "Use the validate_pattern tool to check pattern syntax",
            ]
        )

    elif isinstance(error, SlugKitRateLimitError):
        # Provide context-specific suggestions based on rate limit reason
        reason = getattr(error, 'rate_limit_reason', None) if hasattr(error, 'rate_limit_reason') else None

        if reason == 'not-available':
            # Feature not available
            suggestions.extend(
                [
                    "This feature is not available with your current subscription",
                    "Check your subscription plan and limits",
                    "Contact support to enable this feature",
                    "Consider upgrading your subscription plan",
                ]
            )
        elif reason == 'request-size-exceeded':
            # Request size too large
            suggestions.extend(
                [
                    "Your request size exceeds the maximum allowed",
                    "Reduce the number of items in your request",
                    "Split large requests into smaller batches",
                    "Check the API documentation for size limits",
                ]
            )
        elif reason in {'monthly-limit-exceeded', 'lifetime-limit-exceeded'}:
            # Long-term limits without accurate retry-after
            limit_type = 'monthly' if reason == 'monthly-limit-exceeded' else 'lifetime'
            suggestions.extend(
                [
                    f"You have reached your {limit_type} quota",
                    "Wait until the next billing period or quota reset" if limit_type == 'monthly' else "Your lifetime quota has been exhausted",
                    "Check your usage dashboard for quota renewal date",
                    "Consider upgrading to a plan with higher limits",
                    "Retrying will not help until quotas reset",
                ]
            )
        elif reason in {'rate-limit-exceeded', 'daily-limit-exceeded'}:
            # Short-term token bucket limits with accurate retry-after
            limit_type = 'rate' if reason == 'rate-limit-exceeded' else 'daily'
            retry_after = getattr(error, 'retry_after', None) if hasattr(error, 'retry_after') else None
            if retry_after and retry_after > 0:
                suggestions.extend(
                    [
                        f"{limit_type.capitalize()} limit will reset in {retry_after} seconds",
                        "The SDK will automatically retry with proper backoff",
                        "Reduce request frequency to stay within limits",
                        "Check your current quota status",
                    ]
                )
            else:
                suggestions.extend(
                    [
                        f"You have exceeded your {limit_type} limit",
                        "The SDK will automatically retry with proper backoff",
                        "Reduce request frequency to stay within limits",
                        "Check your current usage limits and quotas",
                    ]
                )
        elif reason == 'redis-error':
            # Server-side Redis error
            suggestions.extend(
                [
                    "A server-side error occurred while checking rate limits",
                    "This is a temporary server issue, not a client problem",
                    "Try again in a few moments",
                    "Contact support if the issue persists",
                ]
            )
        else:
            # Unknown or unspecified reason - generic advice
            suggestions.extend(
                [
                    "Wait before making additional requests",
                    "Reduce request frequency",
                    "Check your current usage limits and quotas",
                    "Review the rate limit reason for more details",
                ]
            )

    elif isinstance(error, SlugKitServerError):
        suggestions.extend(
            [
                "Try again in a few moments",
                "Check the service status page",
                "Contact support if the issue persists",
                "Verify the request is not too complex",
            ]
        )

    elif isinstance(error, SlugKitTimeoutError):
        suggestions.extend(
            [
                "Check your network connection",
                "Try again with a longer timeout",
                "Reduce request complexity if possible",
                "Verify server responsiveness",
            ]
        )

    elif isinstance(error, SlugKitQuotaError):
        suggestions.extend(
            [
                "Check your current usage and limits",
                "Consider upgrading your plan if needed",
                "Review usage patterns and optimize",
                "Contact support for quota increases",
            ]
        )

    else:
        suggestions.extend(
            [
                "Review the error message for specific details",
                "Check the API documentation",
                "Try with simpler parameters first",
                "Contact support if the issue persists",
            ]
        )

    return suggestions


def categorize_error(error: SlugKitError) -> dict[str, Any]:
    """Categorize an error for better understanding and handling."""
    if isinstance(error, SlugKitConnectionError):
        severity = ErrorSeverity.HIGH
        category = "connectivity"
        retryable = True
    elif isinstance(error, SlugKitAuthenticationError):
        severity = ErrorSeverity.CRITICAL
        category = "authentication"
        retryable = False
    elif isinstance(error, SlugKitClientError):
        severity = ErrorSeverity.MEDIUM
        category = "client"
        retryable = False
    elif isinstance(error, SlugKitServerError):
        severity = ErrorSeverity.HIGH
        category = "server"
        retryable = True
    elif isinstance(error, SlugKitRateLimitError):
        severity = ErrorSeverity.MEDIUM
        category = "rate_limit"
        retryable = True
    elif isinstance(error, SlugKitValidationError):
        severity = ErrorSeverity.LOW
        category = "validation"
        retryable = False
    elif isinstance(error, SlugKitTimeoutError):
        severity = ErrorSeverity.MEDIUM
        category = "timeout"
        retryable = True
    elif isinstance(error, SlugKitQuotaError):
        severity = ErrorSeverity.HIGH
        category = "quota"
        retryable = False
    elif isinstance(error, SlugKitConfigurationError):
        severity = ErrorSeverity.CRITICAL
        category = "configuration"
        retryable = False
    else:
        severity = ErrorSeverity.MEDIUM
        category = "unknown"
        retryable = False

    return {
        "severity": severity.value,
        "category": category,
        "retryable": retryable,
        "suggestions": get_error_recovery_suggestions(error),
    }


def extract_error_info(response_text: str) -> tuple[str, dict]:
    """Extract error message and details from server response.

    Args:
        response_text: Raw response text from server

    Returns:
        Tuple of (error_message, error_details)
    """
    if not response_text:
        return f"HTTP {response_text}", {}

    # Try to parse JSON error response
    try:
        if response_text.strip().startswith("{"):
            error_data = json.loads(response_text)
            error_message = error_data.get("message", response_text)
            error_details = {
                "code": error_data.get("code"),
            }
            return error_message, error_details
        else:
            return response_text, {}
    except (ValueError, KeyError, json.JSONDecodeError):
        # Fallback to raw response text
        return response_text, {}


def handle_http_error(
    error: "httpx.HTTPStatusError",
    operation: str,
    endpoint: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs,
) -> Exception:
    """Convert HTTP errors to appropriate SlugKit exceptions with context.

    This is a free function that can be used by any class that needs error handling.

    Args:
        error: The httpx.HTTPStatusError that occurred
        operation: Description of the operation being performed
        endpoint: The API endpoint that was called
        base_url: The base URL of the API
        **kwargs: Additional context information

    Returns:
        An appropriate SlugKit exception with full context
    """
    context = ErrorContext(operation=operation, endpoint=endpoint, base_url=base_url, **kwargs)

    # Extract server response information
    status_code = error.response.status_code

    # Safely read response text (handle streaming responses)
    try:
        response_text = error.response.text.strip()
    except httpx.ResponseNotRead:
        # For streaming responses, we need to read the content first
        try:
            response_body = error.response.read()
            # Decode bytes to string
            response_text = response_body.decode('utf-8').strip() if response_body else ""
        except Exception as read_error:
            # If reading fails, use a default error message
            import logging
            logging.debug(f"Failed to read error response body: {read_error}")
            response_text = ""

    # Extract error message and details from server response
    error_message, error_details = extract_error_info(response_text)

    # If we got an empty error message, use a meaningful default with status code
    if not error_message or error_message.startswith("HTTP "):
        error_message = f"HTTP {status_code}: {error.response.reason_phrase}"

    # Add error details to context if available
    if error_details:
        for key, value in error_details.items():
            if value is not None:
                setattr(context, key, value)

    # Extract rate limiting headers for 429 errors
    rate_limit_info = {}
    if status_code == 429:
        headers = error.response.headers

        # Helper function to parse integer headers with -1 for unlimited
        def parse_int_header(value):
            if value is None:
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        rate_limit_info = {
            'retry_after': parse_int_header(headers.get('X-Slug-Retry-After')),
            'rate_limit_reason': headers.get('X-Slug-Rate-Limit-Reason'),
            'rpm_remaining': parse_int_header(headers.get('X-Slug-Rpm-Remaining')),
            'daily_remaining': parse_int_header(headers.get('X-Slug-Daily-Remaining')),
            'monthly_remaining': parse_int_header(headers.get('X-Slug-Monthly-Remaining')),
            'lifetime_remaining': parse_int_header(headers.get('X-Slug-Lifetime-Remaining')),
        }

        # Add rate limit info to context as well
        for key, value in rate_limit_info.items():
            if value is not None:
                setattr(context, key, value)

    # Create appropriate exception based on status code
    if status_code == 401:
        return SlugKitAuthenticationError(error_message, cause=error, context=context)
    elif status_code == 403:
        return SlugKitAuthenticationError(error_message, cause=error, context=context)
    elif status_code == 404:
        return SlugKitClientError(error_message, cause=error, context=context)
    elif status_code == 400:
        return SlugKitValidationError(error_message, cause=error, context=context)
    elif status_code == 429:
        return SlugKitRateLimitError(error_message, cause=error, context=context, **rate_limit_info)
    elif status_code >= 500:
        return SlugKitServerError(error_message, cause=error, context=context)
    else:
        return SlugKitClientError(error_message, cause=error, context=context)


def should_retry_error(error: Exception) -> bool:
    """Determine if an error should trigger a retry."""
    # Retry on connection errors, timeouts, and 5xx server errors
    if isinstance(error, (httpx.ConnectError, httpx.TimeoutException)):
        return True

    # Retry on SlugKit connection errors
    if isinstance(error, SlugKitConnectionError):
        return True

    # Retry on 5xx server errors (server issues)
    if isinstance(error, httpx.HTTPStatusError):
        return 500 <= error.response.status_code < 600

    # Retry on rate limit errors, but only if it's actually temporary and feasible
    if isinstance(error, SlugKitRateLimitError):
        if hasattr(error, 'rate_limit_reason') and error.rate_limit_reason:
            reason = error.rate_limit_reason

            # These reasons indicate permanent unavailability - never retry
            permanent_unavailable = {
                'not-available',              # Feature not available to user
                'request-size-exceeded',      # Request size exceeds limits (won't succeed on retry)
            }
            if reason in permanent_unavailable:
                return False

            # Only retry for token-bucket based limits with proper retry-after calculation
            # Rate-limit-exceeded (RPM) and daily-limit-exceeded have accurate retry-after
            retryable_limits = {
                'rate-limit-exceeded',        # RPM limit (token bucket with accurate retry-after)
                'daily-limit-exceeded',       # Daily limit (token bucket with accurate retry-after)
            }
            if reason in retryable_limits:
                return True

            # Don't retry for long-term limits without accurate retry-after
            non_retryable_limits = {
                'monthly-limit-exceeded',     # Monthly quota (no accurate retry-after)
                'lifetime-limit-exceeded',    # Lifetime quota (no accurate retry-after)
            }
            if reason in non_retryable_limits:
                return False

            # Redis errors might be transient, but it's a server issue - don't retry
            # The server should handle this, not the client
            if reason == 'redis-error':
                return False

            # Unknown reason - don't retry to be safe
            return False

        # If no reason specified, assume it's retryable (backward compatibility)
        return True

    return False


def calculate_backoff_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay with jitter."""
    import random

    # Exponential backoff: base_delay * 2^(attempt-1)
    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)

    # Add jitter (±25% random variation)
    jitter = random.uniform(0.75, 1.25)
    delay = delay * jitter

    return delay


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_errors: tuple[type[Exception], ...] | None = None,
):
    """Decorator that adds retry logic with exponential backoff to functions."""

    def decorator(func):
        import functools
        import asyncio

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    # Check if we should retry
                    if retryable_errors:
                        should_retry = isinstance(e, retryable_errors)
                    else:
                        should_retry = should_retry_error(e)

                    if not should_retry or attempt == max_attempts:
                        break

                    # Calculate delay and wait
                    delay = calculate_backoff_delay(attempt, base_delay, max_delay)
                    import time

                    time.sleep(delay)

            # Re-raise the last error
            raise last_error

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e

                    # Check if we should retry
                    if retryable_errors:
                        should_retry = isinstance(e, retryable_errors)
                    else:
                        should_retry = should_retry_error(e)

                    if not should_retry or attempt == max_attempts:
                        break

                    # Calculate delay and wait
                    delay = calculate_backoff_delay(attempt, base_delay, max_delay)
                    await asyncio.sleep(delay)

            # Re-raise the last error
            raise last_error

        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
