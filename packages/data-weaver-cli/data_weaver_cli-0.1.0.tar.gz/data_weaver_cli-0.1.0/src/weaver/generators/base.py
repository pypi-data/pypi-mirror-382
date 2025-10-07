"""
Base generator class for Weaver project scaffolding.

This provides the abstract interface and common functionality
for all project generators (cookiecutter, custom, etc.).
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from src.weaver.config import Config
import subprocess
import os
import shutil
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

console = Console()


@dataclass
class GenerationResult:
    """Result of project generation"""
    success: bool
    project_path: Optional[Path] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    created_files: List[Path] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)


class BaseGenerator(ABC):
    """Abstract base class for all project generators"""

    def __init__(self):
        self.console = Console()

    @abstractmethod
    def generate(self, config: Config) -> GenerationResult:
        """Generate a project based on the configuration"""
        pass

    @abstractmethod
    def validate_config(self, config: Config) -> List[str]:
        """Validate configuration and return list of errors"""
        pass

    @abstractmethod
    def get_dependencies(self, config: Config) -> List[str]:
        """Get list of required dependencies for this configuration"""
        pass

    def pre_generate_hook(self, config: Config) -> bool:
        """Hook called before generation starts. Return False to cancel."""
        return True

    def post_generate_hook(self, config: Config, result: GenerationResult) -> None:
        """Hook called after generation completes"""
        if result.success and result.project_path:
            self._setup_git_repo(result.project_path)
            self._create_initial_commit(result.project_path, config)

    def _setup_git_repo(self, project_path: Path) -> None:
        """Initialize git repository"""
        try:
            subprocess.run(
                ["git", "init"],
                cwd=project_path,
                capture_output=True,
                check=True
            )
            rprint(f"✅ Initialized git repository")
        except subprocess.CalledProcessError as e:
            rprint(f"⚠️ Could not initialize git repo: {e}")

    def _create_initial_commit(self, project_path: Path, config: Config) -> None:
        """Create initial commit"""
        try:
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", f"🕷️ Initial weave of {config.project_name}"],
                cwd=project_path,
                capture_output=True,
                check=True
            )
            rprint(f"✅ Created initial commit")
        except subprocess.CalledProcessError:
            rprint(f"⚠️ Could not create initial commit")

    def _check_directory_exists(self, path: Path) -> bool:
        """Check if directory already exists"""
        return path.exists() and path.is_dir()

    def _create_directory_structure(self, base_path: Path, structure: Dict[str, Any]) -> List[Path]:
        """
        Create directory structure from nested dict.

        Args:
            base_path: Base directory to create structure in
            structure: Dict where keys are dir/file names, values are either:
                      - Dict (subdirectory)
                      - str (file content)
                      - None (empty directory)

        Returns:
            List of created paths
        """
        created_paths = []

        def _create_recursive(current_path: Path, current_structure: Dict[str, Any]):
            for name, content in current_structure.items():
                path = current_path / name

                if isinstance(content, dict):
                    # It's a directory
                    path.mkdir(parents=True, exist_ok=True)
                    created_paths.append(path)
                    _create_recursive(path, content)

                elif isinstance(content, str):
                    # It's a file with content
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content)
                    created_paths.append(path)

                elif content is None:
                    # Empty directory or __init__.py
                    if name.endswith('.py') or '.' in name:
                        # It's a file
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.touch()
                    else:
                        # It's a directory
                        path.mkdir(parents=True, exist_ok=True)
                    created_paths.append(path)

        _create_recursive(base_path, structure)
        return created_paths

    def _install_dependencies(self, project_path: Path, config: Config) -> bool:
        """Install project dependencies"""
        try:
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
            ) as progress:
                task = progress.add_task("Installing dependencies...", total=None)

                # Create virtual environment
                subprocess.run(
                    ["python", "-m", "venv", "venv"],
                    cwd=project_path,
                    capture_output=True,
                    check=True
                )

                # Determine pip path
                if os.name == 'nt':  # Windows
                    pip_path = project_path / "venv" / "Scripts" / "pip"
                else:  # Unix-like
                    pip_path = project_path / "venv" / "bin" / "pip"

                # Install dependencies
                subprocess.run(
                    [str(pip_path), "install", "-e", ".[dev]"],
                    cwd=project_path,
                    capture_output=True,
                    check=True
                )

                progress.update(task, completed=True)

            rprint("✅ Dependencies installed successfully")
            return True

        except subprocess.CalledProcessError as e:
            rprint(f"⚠️ Failed to install dependencies: {e}")
            return False

    def _generate_next_steps(self, config:Config, project_path: Path) -> List[str]:
        """Generate context-aware next steps for the user"""
        steps = [
            f"cd {config.project_slug}",
            "python -m venv venv",
        ]

        # Platform-specific activation
        if os.name == 'nt':
            steps.append("venv\\Scripts\\activate")
        else:
            steps.append("source venv/bin/activate")

        steps.append("pip install -e .[dev]")

        # Docker steps
        if config.use_docker:
            steps.append("docker-compose up -d  # Start services")

        # Database setup
        if config.database == "postgresql":
            steps.append("# Set up PostgreSQL database")
            steps.append("createdb " + config.project_slug)

        # Project-specific steps
        if "api" in config.data_sources:
            steps.append("# Configure API keys in .env")

        if config.orchestrator == "prefect":
            steps.append("prefect server start  # In another terminal")

        # Run the project
        if config.api_framework != "none":
            steps.append(f"python -m {config.project_slug}.api  # Start API server")
        else:
            steps.append(f"python -m {config.project_slug}.cli --help")

        return steps

    def _validate_prerequisites(self) -> List[str]:
        """Check if required tools are installed"""
        errors = []

        # Check Python version
        import sys
        if sys.version_info < (3, 9):
            errors.append("Python 3.9 or higher is required")

        # Check git
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append("Git is required but not installed")

        return errors

    def _backup_existing_directory(self, path: Path) -> Optional[Path]:
        """Create backup of existing directory"""
        if not path.exists():
            return None

        backup_path = path.with_suffix(f".backup.{path.name}")
        counter = 1
        while backup_path.exists():
            backup_path = path.with_suffix(f".backup.{path.name}.{counter}")
            counter += 1

        shutil.move(str(path), str(backup_path))
        rprint(f"📦 Backed up existing directory to {backup_path}")
        return backup_path


class GeneratorError(Exception):
    """Base exception for generator errors"""
    pass


class ConfigurationError(GeneratorError):
    """Raised when configuration is invalid"""
    pass


class GenerationError(GeneratorError):
    """Raised when generation fails"""
    pass


class PrerequisiteError(GeneratorError):
    """Raised when prerequisites are not met"""
    pass