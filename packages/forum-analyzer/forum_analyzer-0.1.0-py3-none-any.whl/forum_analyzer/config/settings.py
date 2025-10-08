"""Configuration settings using Pydantic."""

import os
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """API configuration."""

    base_url: str
    rate_limit: float = 1.0
    timeout: float = 30.0
    max_retries: int = 3
    category_path: str


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = "sqlite:///data/database/forum.db"
    echo: bool = False


class ScrapingSettings(BaseSettings):
    """Scraping configuration."""

    batch_size: int = 100
    checkpoint_interval: int = 10
    checkpoint_dir: str = "data/checkpoints"


class CategoryConfig(BaseSettings):
    """Category configuration."""

    id: int
    name: Optional[str] = None
    slug: Optional[str] = None


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/forum_analyzer.log"


class AskSettings(BaseSettings):
    """Settings for the ask command."""

    context_limit: int = 50
    cache_queries: bool = True


class LLMAnalysisSettings(BaseSettings):
    """LLM analysis settings."""

    api_key: str = ""
    model: str = "claude-opus-4"
    batch_size: int = 10
    max_tokens: int = 4096
    temperature: float = 0.0
    theme_context_limit: int = 50
    context_char_limit: int = 15000  # Max characters for analysis context
    ask: AskSettings = Field(default_factory=AskSettings)


class Settings(BaseSettings):
    """Main application settings."""

    api: APISettings = Field(default_factory=APISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    scraping: ScrapingSettings = Field(default_factory=ScrapingSettings)
    categories: List[CategoryConfig] = Field(default_factory=list)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    llm_analysis: LLMAnalysisSettings = Field(
        default_factory=LLMAnalysisSettings
    )

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Settings":
        """Load settings from YAML file.

        Args:
            config_path: Path to YAML config file

        Returns:
            Settings instance
        """
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        return cls(
            api=APISettings(**config_data.get("api", {})),
            database=DatabaseSettings(**config_data.get("database", {})),
            scraping=ScrapingSettings(**config_data.get("scraping", {})),
            categories=[
                CategoryConfig(**cat)
                for cat in config_data.get("categories", [])
            ],
            logging=LoggingSettings(**config_data.get("logging", {})),
            llm_analysis=LLMAnalysisSettings(
                **config_data.get("llm_analysis", {})
            ),
        )


_settings: Optional[Settings] = None
_project_dir: Optional[Path] = None


def get_project_dir() -> Path:
    """Get the project directory from context or environment.

    Returns:
        Path to the project directory
    """
    global _project_dir

    if _project_dir is not None:
        return _project_dir

    # Check environment variable
    env_dir = os.getenv("FORUM_ANALYZER_DIR")
    if env_dir:
        return Path(env_dir).resolve()

    # Default to current directory
    return Path.cwd()


def set_project_dir(project_dir: Path) -> None:
    """Set the global project directory context.

    Args:
        project_dir: Path to the project directory
    """
    global _project_dir
    _project_dir = project_dir.resolve()


def reset_settings() -> None:
    """Reset the settings singleton (useful for testing)."""
    global _settings, _project_dir
    _settings = None
    _project_dir = None


def get_settings(project_dir: Optional[Path] = None) -> Settings:
    """Get application settings from project directory.

    Args:
        project_dir: Optional project directory (defaults to get_project_dir())

    Returns:
        Settings instance with paths resolved relative to project directory

    Raises:
        FileNotFoundError: If config file doesn't exist in project directory
    """
    global _settings

    if _settings is None:
        if project_dir is None:
            project_dir = get_project_dir()
        else:
            project_dir = project_dir.resolve()

        config_path = project_dir / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Not a forum-analyzer project directory.\n"
                f"Run 'forum-analyzer init' to initialize a project."
            )

        _settings = Settings.from_yaml(config_path)

        # Resolve all paths relative to project directory
        # Database path
        db_url = _settings.database.url
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            if not Path(db_path).is_absolute():
                _settings.database.url = f"sqlite:///{project_dir / db_path}"

        # Checkpoint directory
        if not Path(_settings.scraping.checkpoint_dir).is_absolute():
            _settings.scraping.checkpoint_dir = str(
                project_dir / _settings.scraping.checkpoint_dir
            )

        # Logging file
        if not Path(_settings.logging.file).is_absolute():
            _settings.logging.file = str(project_dir / _settings.logging.file)

    return _settings
