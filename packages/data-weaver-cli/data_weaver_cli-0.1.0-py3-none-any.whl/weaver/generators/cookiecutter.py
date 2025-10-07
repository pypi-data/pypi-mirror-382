"""
Cookiecutter-based project generator for Weaver.

This generator uses your actual cookiecutter template at:
https://github.com/adrianmoses/entity-resolution-cookiecutter
"""
from pathlib import Path
from typing import Dict, List, Any
from src.weaver.config import Config
import subprocess
import shutil

from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import CookiecutterException
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from .base import (
    BaseGenerator,
    GenerationResult
)

class CookiecutterGenerator(BaseGenerator):
    """Generator that uses your entity-resolution-cookiecutter template"""

    # Your actual template repository
    TEMPLATE_REPO = "https://github.com/adrianmoses/entity-resolution-cookiecutter"

    # Template mappings based on your cookiecutter structure
    TEMPLATE_MAPPINGS = {
        "advanced-search": {
            "repo": TEMPLATE_REPO,
            "description": "Hybrid sparse and vector search",
            "context_overrides": {
                "include_vector_search": True,
                "data_sources": "api,datasets",
                "database": "postgresql"
            }
        },
        "knowledge-graph": {
            "repo": TEMPLATE_REPO,
            "description": "AI company knowledge graph",
            "context_overrides": {
                "include_vector_search": False,
                "data_sources": "web_scraping,api,github",
                "database": "neo4j"
            }
        },
        "news-analyzer": {
            "repo": TEMPLATE_REPO,
            "description": "News aggregator with bias analysis",
            "context_overrides": {
                "include_vector_search": True,
                "data_sources": "rss,web_scraping",
                "database": "postgresql",
                "include_nlp": True
            }
        },
        "basic": {
            "repo": TEMPLATE_REPO,
            "description": "Basic entity-relationship project",
            "context_overrides": {
                "include_vector_search": False,
                "data_sources": "api",
                "database": "sqlite"
            }
        }
    }

    def __init__(self):
        super().__init__()

    def generate(self, config: Config) -> GenerationResult:
        """Generate a project using your cookiecutter template"""

        try:
            # Validate prerequisites
            prereq_errors = self._validate_prerequisites()
            if prereq_errors:
                return GenerationResult(
                    success=False,
                    error_message=f"Prerequisites not met: {', '.join(prereq_errors)}"
                )

            # Validate configuration
            config_errors = self.validate_config(config)
            if config_errors:
                return GenerationResult(
                    success=False,
                    error_message=f"Configuration errors: {', '.join(config_errors)}"
                )

            # Pre-generation hook
            if not self.pre_generate_hook(config):
                return GenerationResult(
                    success=False,
                    error_message="Pre-generation hook failed"
                )

            # Prepare cookiecutter context for your template
            extra_context = self._prepare_cookiecutter_context(config)

            # Set output directory
            project_path = Path(config.project_slug)

            # Check if a project directory already exists
            if self._check_directory_exists(project_path):
                backup_path = self._backup_existing_directory(project_path)

            # Generate a project with progress indication
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
            ) as progress:
                task = progress.add_task("🕷️ Weaving project structure...", total=None)

                try:
                    # Run cookiecutter with your template
                    result_path = cookiecutter(
                        self.TEMPLATE_REPO,
                        extra_context=extra_context,
                        no_input=True,  # Use provided context without prompting
                        overwrite_if_exists=True
                    )

                    project_path = Path(result_path)
                    progress.update(task, completed=True)

                except CookiecutterException as e:
                    return GenerationResult(
                        success=False,
                        error_message=f"Cookiecutter generation failed: {str(e)}"
                    )

            # Post-process the generated project
            warnings = self._post_process_project(config, project_path)

            # Collect created files
            created_files = list(project_path.rglob("*")) if project_path.exists() else []

            # Generate next steps
            next_steps = self._generate_next_steps(config, project_path)

            # Create result
            result = GenerationResult(
                success=True,
                project_path=project_path,
                created_files=created_files,
                next_steps=next_steps,
                warnings=warnings
            )

            # Post-generation hook
            self.post_generate_hook(config, result)

            return result

        except Exception as e:
            return GenerationResult(
                success=False,
                error_message=f"Unexpected error during generation: {str(e)}"
            )

    def _prepare_cookiecutter_context(self, config: Config) -> Dict[str, Any]:
        """Prepare context dictionary for your cookiecutter template"""

        # Start with base context that matches your cookiecutter.json
        context = {
            "project_name": config.project_name,
            "project_slug": config.project_slug,
            "description": config.description,
            "author_name": config.author_name,
            "email": config.author_email,
            "use_pytest": "yes",
        }

        # Map our config to your cookiecutter variables
        # (Based on common cookiecutter patterns - adjust to match your actual cookiecutter.json)

        # Data sources - convert list to comma-separated string if needed
        if isinstance(config.data_sources, list):
            context["data_sources"] = ",".join(config.data_sources)
        else:
            context["data_sources"] = config.data_sources

        # Storage backend
        context["database"] = config.database

        # Pipeline orchestrator
        context["orchestrator"] = config.orchestrator

        # API framework
        context["api_framework"] = config.api_framework

        # Feature flags
        context["use_docker"] = "yes" if config.use_docker else "no"
        context["include_nlp"] = "yes" if config.include_nlp else "no"
        context["include_vector_search"] = "yes" if config.include_vector_search else "n"

        # Search engine
        if config.search_engine:
            context["search_engine"] = config.search_engine
        else:
            context["search_engine"] = "none"

        return context

    def validate_config(self, config: Config) -> List[str]:
        """Validate configuration for your cookiecutter template"""
        errors = []

        # Basic validation
        if not config.project_name:
            errors.append("Project name is required")

        if not config.project_slug:
            errors.append("Project slug is required")

        if not config.author_name:
            errors.append("Author name is required")

        # Data source validation
        if not config.data_sources:
            errors.append("At least one data source must be specified")

        valid_data_sources = ["api", "web_scraping", "datasets"]
        if isinstance(config.data_sources, list):
            invalid_sources = set(config.data_sources) - set(valid_data_sources)
            if invalid_sources:
                errors.append(f"Invalid data sources: {', '.join(invalid_sources)}")

        # Storage backend validation
        valid_backends = ["postgresql", "sqlite", "neo4j", "mongodb"]
        if config.database not in valid_backends:
            errors.append(f"Invalid storage backend: {config.database}. Must be one of: {', '.join(valid_backends)}")

        # Vector search validation
        if config.include_vector_search and config.database not in ["postgresql"]:
            errors.append("Vector search currently only supported with PostgreSQL + pgvector")

        # Pipeline orchestrator validation
        valid_orchestrators = ["prefect", "airflow"]
        if config.orchestrator not in valid_orchestrators:
            errors.append(f"Invalid pipeline orchestrator: {config.orchestrator}")

        # API framework validation
        valid_apis = ["fastapi", "flask", "django", "none"]
        if config.api_framework not in valid_apis:
            errors.append(f"Invalid API framework: {config.api_framework}")

        return errors

    def get_dependencies(self, config: Config) -> List[str]:
        """Get Python dependencies based on configuration"""
        deps = [
            "python-dotenv>=1.0.0",
            "pydantic>=2.0.0",
            "pydantic-settings>=2.0.0",
            "typer>=0.9.0",
            "rich>=13.0.0",
            "loguru>=0.7.0",
            "pandas>=2.0.0"
        ]

        # Data source dependencies
        if "web_scraping" in config.data_sources:
            deps.extend([
                "requests>=2.31.0",
                "beautifulsoup4>=4.12.0",
                "scrapy>=2.10.0",
                "selenium>=4.15.0"
            ])

        if "api" in config.data_sources:
            deps.extend([
                "httpx>=0.25.0",
                "aiohttp>=3.9.0"
            ])

        if "rss" in config.data_sources:
            deps.append("feedparser>=6.0.0")

        # Storage dependencies
        if config.database == "postgresql":
            deps.extend([
                "psycopg2-binary>=2.9.0",
                "sqlalchemy>=2.0.0",
                "alembic>=1.12.0"
            ])
            if config.include_vector_search:
                deps.append("pgvector>=0.2.0")

        elif config.database == "neo4j":
            deps.extend([
                "neo4j>=5.14.0",
                "py2neo>=2022.1.0"
            ])

        elif config.database == "mongodb":
            deps.extend([
                "motor>=3.3.0",
                "pymongo>=4.6.0"
            ])

        elif config.database == "sqlite":
            deps.extend([
                "sqlalchemy>=2.0.0",
                "aiosqlite>=0.19.0"
            ])

        # Search engine dependencies
        if config.search_engine == "elasticsearch":
            deps.append("elasticsearch>=8.11.0")
        elif config.search_engine == "vector_hybrid":
            deps.extend([
                "qdrant-client>=1.7.0",
            ])

        # Pipeline dependencies
        if config.orchestrator == "prefect":
            deps.append("prefect>=2.14.0")
        elif config.orchestrator == "airflow":
            deps.append("apache-airflow>=2.7.0")

        # API framework dependencies
        if config.api_framework == "fastapi":
            deps.extend([
                "fastapi>=0.104.0",
                "uvicorn[standard]>=0.24.0"
            ])
        elif config.api_framework == "flask":
            deps.extend([
                "flask>=3.0.0",
                "flask-cors>=4.0.0"
            ])
        elif config.api_framework == "django":
            deps.extend([
                "django>=4.2.0",
                "djangorestframework>=3.14.0"
            ])

        # NLP dependencies
        if config.include_nlp:
            deps.extend([
                "spacy>=3.7.0",
                "transformers>=4.35.0",
                "torch>=2.1.0",
                "scikit-learn>=1.3.0"
            ])

        # Vector search dependencies
        if config.include_vector_search:
            deps.extend([
                "sentence-transformers>=2.2.0",
                "numpy>=1.24.0",
                "faiss-cpu>=1.7.4"
            ])

        return sorted(set(deps))  # Remove duplicates and sort

    def _post_process_project(self, config: Config, project_path: Path) -> List[str]:
        """Post-process the generated project"""
        warnings = []

        try:
            # Create .env file from .env.example if it exists
            env_example = project_path / ".env.example"
            env_file = project_path / ".env"
            if env_example.exists() and not env_file.exists():
                shutil.copy(env_example, env_file)
                rprint("✅ Created .env file from template")

            # Set up pre-commit hooks if config exists
            pre_commit_config = project_path / ".pre-commit-config.yaml"
            if pre_commit_config.exists():
                try:
                    subprocess.run(
                        ["pre-commit", "install"],
                        cwd=project_path,
                        capture_output=True,
                        check=True
                    )
                    rprint("✅ Installed pre-commit hooks")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    warnings.append("Could not install pre-commit hooks (pre-commit not installed)")

        except Exception as e:
            warnings.append(f"Post-processing error: {str(e)}")

        return warnings


    def list_available_templates(self) -> Dict[str, Dict[str, str]]:
        """List all available templates"""
        return {
            name: {
                "description": info["description"],
                "repo": info["repo"]
            }
            for name, info in self.TEMPLATE_MAPPINGS.items()
        }

    def _validate_prerequisites(self) -> List[str]:
        """Validate cookiecutter-specific prerequisites"""
        errors = super()._validate_prerequisites()

        # Check if cookiecutter is installed
        try:
            import cookiecutter
        except ImportError:
            errors.append("cookiecutter package is required but not installed (pip install cookiecutter)")

        return errors
