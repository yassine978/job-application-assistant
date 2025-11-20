"""
Sentry Configuration for Error Tracking and Monitoring

This module configures Sentry for the Job Application Assistant.
Sentry provides real-time error tracking, performance monitoring, and release tracking.

Setup:
1. Create account at https://sentry.io
2. Create new Python project
3. Copy DSN to .env file: SENTRY_DSN=your_dsn_here
4. Import this module in your main application files
"""

import os
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

# Get configuration from environment
SENTRY_DSN = os.getenv("SENTRY_DSN")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
RELEASE_VERSION = os.getenv("RELEASE_VERSION", "unknown")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


def initialize_sentry():
    """
    Initialize Sentry SDK with proper configuration.

    Call this function at the start of your application:

    Example:
        from monitoring.sentry_config import initialize_sentry
        initialize_sentry()
    """
    if not SENTRY_DSN:
        logging.warning(
            "[WARNING] SENTRY_DSN not found in environment. "
            "Error tracking is disabled."
        )
        return

    # Configure logging integration
    logging_integration = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    # Initialize Sentry
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100% of transactions
        # In production, consider lowering this to save quota (e.g., 0.1 for 10%)
        traces_sample_rate=1.0 if DEBUG else 0.1,
        # Set profiles_sample_rate to profile a subset of transactions
        profiles_sample_rate=1.0 if DEBUG else 0.1,
        environment=ENVIRONMENT,
        release=RELEASE_VERSION,
        # Integrations
        integrations=[
            SqlalchemyIntegration(),
            logging_integration,
        ],
        # Send default PII (Personally Identifiable Information)
        send_default_pii=False,
        # Before send hook to filter sensitive data
        before_send=before_send_hook,
        # Attach stack traces to messages
        attach_stacktrace=True,
        # Maximum breadcrumbs
        max_breadcrumbs=50,
    )

    logging.info(
        f"[OK] Sentry initialized for environment: {ENVIRONMENT}, "
        f"release: {RELEASE_VERSION}"
    )


def before_send_hook(event, hint):
    """
    Filter and modify events before sending to Sentry.

    This hook can be used to:
    - Filter out sensitive data
    - Add custom tags or context
    - Skip certain events

    Args:
        event: The event dictionary
        hint: Additional information about the event

    Returns:
        Modified event or None to skip the event
    """
    # Filter out sensitive environment variables
    if "server_name" in event:
        event.pop("server_name", None)

    # Remove sensitive data from extra context
    if "extra" in event:
        sensitive_keys = ["password", "api_key", "token", "secret"]
        for key in sensitive_keys:
            event["extra"].pop(key, None)

    # Skip events with specific error messages (if needed)
    if "exception" in event:
        for exception in event["exception"].get("values", []):
            if exception.get("value", "").startswith("Test error"):
                return None  # Skip test errors

    return event


def add_breadcrumb(message, category="info", level="info", data=None):
    """
    Add a breadcrumb to the current Sentry scope.

    Breadcrumbs are a trail of events that led to an error.

    Args:
        message: Breadcrumb message
        category: Category of the breadcrumb (e.g., 'database', 'http', 'ui')
        level: Severity level ('debug', 'info', 'warning', 'error')
        data: Additional data dictionary

    Example:
        add_breadcrumb(
            message="User searched for jobs",
            category="search",
            data={"keywords": "Python Developer", "location": "Paris"}
        )
    """
    sentry_sdk.add_breadcrumb(
        message=message, category=category, level=level, data=data or {}
    )


def set_user_context(user_id=None, username=None, email=None, **kwargs):
    """
    Set user context for error tracking.

    This helps identify which user encountered an error.

    Args:
        user_id: User ID
        username: Username
        email: User email (will be filtered if send_default_pii=False)
        **kwargs: Additional user properties

    Example:
        set_user_context(
            user_id="123",
            username="john_doe",
            subscription="premium"
        )
    """
    user_data = {"id": user_id, "username": username, "email": email, **kwargs}
    # Remove None values
    user_data = {k: v for k, v in user_data.items() if v is not None}
    sentry_sdk.set_user(user_data)


def set_context(name, data):
    """
    Set custom context for error events.

    Args:
        name: Context name
        data: Context data dictionary

    Example:
        set_context("job_search", {
            "keywords": ["Python", "Developer"],
            "location": "Paris",
            "results_count": 42
        })
    """
    sentry_sdk.set_context(name, data)


def capture_exception(exception, level="error", **kwargs):
    """
    Manually capture an exception.

    Args:
        exception: The exception to capture
        level: Severity level ('fatal', 'error', 'warning', 'info', 'debug')
        **kwargs: Additional context

    Example:
        try:
            risky_operation()
        except Exception as e:
            capture_exception(e, level="error", extra={"operation": "risky"})
    """
    with sentry_sdk.push_scope() as scope:
        scope.level = level
        for key, value in kwargs.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_exception(exception)


def capture_message(message, level="info", **kwargs):
    """
    Capture a message event.

    Args:
        message: The message to capture
        level: Severity level
        **kwargs: Additional context

    Example:
        capture_message(
            "Job scraping completed",
            level="info",
            extra={"jobs_scraped": 150}
        )
    """
    with sentry_sdk.push_scope() as scope:
        scope.level = level
        for key, value in kwargs.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_message(message)


def start_transaction(name, op="task"):
    """
    Start a performance transaction.

    Args:
        name: Transaction name
        op: Operation type (e.g., 'task', 'http', 'db.query')

    Returns:
        Transaction object (use as context manager)

    Example:
        with start_transaction("scrape_jobs", op="task"):
            jobs = scraper.scrape_all_sources()
    """
    return sentry_sdk.start_transaction(name=name, op=op)


def start_span(operation, description=None):
    """
    Start a span within a transaction.

    Args:
        operation: Operation name (e.g., 'db.query', 'http.request')
        description: Span description

    Returns:
        Span object (use as context manager)

    Example:
        with start_transaction("process_jobs"):
            with start_span("db.query", "Fetch jobs from database"):
                jobs = session.query(Job).all()
            with start_span("ai.generation", "Generate CV"):
                cv = generator.generate_cv(job)
    """
    return sentry_sdk.start_span(op=operation, description=description)


# Example usage in application
if __name__ == "__main__":
    # This demonstrates how to use Sentry monitoring
    initialize_sentry()

    # Add breadcrumbs
    add_breadcrumb("Application started", category="lifecycle")

    # Set user context
    set_user_context(user_id="demo_user", username="demo")

    # Capture a test message
    capture_message("Test message from Sentry config", level="info")

    # Example transaction with spans
    with start_transaction("example_task", op="task"):
        add_breadcrumb("Starting example task", category="task")

        with start_span("step_1", "First step of task"):
            # Simulate work
            import time

            time.sleep(0.1)

        with start_span("step_2", "Second step of task"):
            # Simulate work
            time.sleep(0.1)

    print("[OK] Sentry configuration test completed")
