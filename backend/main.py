"""Socrates Study Assistant - Main entrypoint."""
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
import uvicorn
from vyper import v

import common.injectors as injectors
from infrastructure.api.fastapi.app_builder import AppBuilder


def _configure_logger() -> None:
    """Configure application logging."""
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )


def load_dotenv_config() -> None:
    """Load configuration from .env file if present."""
    load_dotenv()


def load_vyper_config() -> None:
    """Load configuration files from paths using Vyper."""
    config_paths = [Path("."), Path("..")]

    v.set_env_key_replacer(".", "_")
    v.set_config_type("yaml")
    v.set_config_name("config")

    for path in config_paths:
        v.add_config_path(str(path))

    try:
        v.read_in_config()
        logging.info("[Bootstrap] Configuration file loaded successfully")
    except Exception as e:
        logging.warning(
            "[Bootstrap] No configuration file found: %s. Using environment variables and defaults.",
            e,
        )

    # Enable automatic environment variable reading
    v.automatic_env()


def set_config_defaults() -> None:
    """Set default configuration values."""
    # OpenAI settings
    v.set_default("openai.api_key", "")
    v.set_default("openai.completion_model", "gpt-4o")
    v.set_default("openai.vision_model", "gpt-4o")

    # Study session settings
    v.set_default("study_session.max_questions", 10)

    # Server settings
    v.set_default("server.host", "0.0.0.0")
    v.set_default("server.port", 8000)
    v.set_default("server.reload", False)


def create_app():
    """Create and configure the FastAPI application."""
    logging.info("[Bootstrap] Initializing Socrates Study Assistant")

    # Load configuration
    _configure_logger()
    load_dotenv_config()
    load_vyper_config()
    set_config_defaults()

    logging.info("[Bootstrap] Initializing API endpoints")

    # Create API implementations using dependency injection
    app_builder = AppBuilder(
        ingest_document_api=injectors.get_ingest_document_api(),
        create_learning_plan_api=injectors.get_create_learning_plan_api(),
        start_study_session_api=injectors.get_start_study_session_api(),
        get_study_session_api=injectors.get_get_study_session_api(),
        submit_answer_api=injectors.get_submit_answer_api(),
        assess_question_api=injectors.get_assess_question_api(),
        update_mastery_api=injectors.get_update_mastery_api(),
    )

    app = app_builder.create_app()

    logging.info("[Bootstrap] Socrates Study Assistant initialized successfully")

    return app

app = create_app()

def main() -> None:
    """Main entrypoint for running the application."""
    # Get server configuration
    host = v.get_string("server.host")
    port = v.get_int("server.port")
    reload = v.get_bool("server.reload")

    logging.info(
        "[Bootstrap] Starting Socrates Study Assistant on %s:%d (reload=%s)",
        host,
        port,
        reload,
    )

    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
