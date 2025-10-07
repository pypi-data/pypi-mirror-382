#!/usr/bin/env python3

"""
Weaver CLI - Spinning up data connections with style! 🕷️

A fun, powerful CLI for scaffolding entity-relationship projects.
"""
import typer
from src.weaver.config import TEMPLATES, Config, create_config
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.weaver.generators.base import GenerationResult
from src.weaver.generators.cookiecutter import CookiecutterGenerator

app = typer.Typer(
    name="weaver",
    help="🕷️ Weave your data into beautiful connections",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
)
console = Console()

# Fun ASCII art
WEAVER_LOGO = """
    🕷️ WEAVER 🕷️
  ╭─────────────────╮
  │  Spinning up    │
  │  connections!   │
  ╰─────────────────╯
"""


def create_advanced_search_project(project_name: Optional[str] = None) -> GenerationResult:
    """Create a Pokémon team builder project"""

    # Create configuration specifically for Pokémon project
    config = create_config(
        project_name=project_name or "pokemon-team-builder",
        project_slug=(project_name or "pokemon-team-builder").lower()\
            .replace(" ", "_")\
            .replace("-", "_"),
        description="Hybrid vector search system for optimal Pokémon team building",
        author_name="Pokemon Trainer",
        author_email="trainer@pokemon.com",

        data_sources=["api", "datasets", "web_scraping"],
        database="postgresql",
        search_engine="vector_hybrid",
        orchestrator="prefect",
        api_framework="fastapi",

        include_api_scraping=False,
        include_web_scraping=True,
        include_vector_search=True,  # Key feature for team optimization
        include_nlp=False,  # Don't need NLP for Pokémon data
        use_docker=True,
        use_pytest=True
    )


    # Show what we're about to create
    show_project_summary(config)

    # Generate the project
    console.print("🕷️ [bold cyan]Starting advanced search project generation...[/bold cyan]")
    gen = CookiecutterGenerator()
    result = gen.generate(config)

    if result.success:
        _show_success_message(config, result)
    else:
        _show_error_message(result)

    return result


@app.command()
def create(
    project_name: Optional[str] = typer.Option(None, "--name", "-n", help="Name of your project"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Project template to use"),
    list_deps: bool = typer.Option(False, "--list-deps", help="Show dependencies without creating project"),
    ):
    """🕷️ Enhanced create command with generator support"""

    # Handle Advanced search template specifically
    if template == "advanced-search":
        if list_deps:
            # Create config to show dependencies
            config = Config()
            config.project_name = project_name or "pokemon-team-builder"
            config.project_slug = project_name.lower().replace("-", "_") or "pokemon_team_builder"
            config.description = "Pokémon team builder"
            config.author_name = "Trainer"
            config.author_email = "trainer@pokemon.com"
            config.data_sources = ["api", "datasets"]
            config.database = "postgresql"
            config.search_engine = "vector_hybrid"
            config.include_vector_search = True
            get_dependencies(config)
            return

        create_advanced_search_project(
            project_name=project_name,
        )

    else:
        # Handle other templates or interactive mode
        console.print("🕷️ Interactive mode not yet implemented")
        console.print("Available templates:")
        list_templates()


@app.command()
def templates():
    """📋 List available project templates"""
    console.print(WEAVER_LOGO, style="cyan bold")
    console.print("Available templates to weave:\n", style="green")

    for template_name, template_info in TEMPLATES.items():
        panel = Panel(
            f"[bold]{template_info['name']}[/bold]\n"
            f"{template_info['description']}\n\n"
            f"[dim]Data: {', '.join(template_info['data_sources'])}\n"
            f"Storage: {template_info['database']}\n"
            f"Pipeline: {template_info['orchestrator']}[/dim]",
            title=f"[cyan]{template_name}[/cyan]",
            border_style="blue"
        )
        console.print(panel)
        console.print()

    console.print(f"[green]Usage:[/green] [cyan]weaver create --template <template-name>[/cyan]")


@app.command()
def list_templates() -> None:
    """List available templates for a generator"""

    gen = CookiecutterGenerator()
    templates = gen.list_available_templates()

    console.print(WEAVER_LOGO, style="cyan bold")
    console.print(f"\n🕷️ [bold cyan]Available Templates[/bold cyan]\n")

    for template_name, template_info in templates.items():
        panel = Panel(
            f"[bold]{template_info.get('description', 'No description')}[/bold]\n"
            f"[dim]Repository: {template_info.get('repo', 'N/A')}\n"
            f"Directory: {template_info.get('directory', 'N/A')}[/dim]",
            title=f"[cyan]{template_name}[/cyan]",
            border_style="blue"
        )
        console.print(panel)


@app.command()
def version():
    """Show weaver version"""
    console.print("🕷️ Weaver CLI v0.1.0")
    console.print("Spinning up data connections with style!")


def get_dependencies(config: Config) -> None:
    """Show dependencies that will be installed"""
    gen = CookiecutterGenerator()
    deps = gen.get_dependencies(config)

    console.print(f"\n📦 [bold cyan]Dependencies for {config.project_name}[/bold cyan]\n")

    # Group dependencies by category
    categories = {
        "Core": [],
        "Data Sources": [],
        "Storage": [],
        "Pipeline": [],
        "API": [],
        "Search": [],
        "NLP": [],
        "Vector Search": [],
        "Development": []
    }

    for dep in deps:
        if any(x in dep.lower() for x in ["request", "scrapy", "beautifulsoup", "httpx", "aiohttp"]):
            categories["Data Sources"].append(dep)
        elif any(x in dep.lower() for x in ["psycopg", "sqlalchemy", "neo4j", "mongo"]):
            categories["Storage"].append(dep)
        elif any(x in dep.lower() for x in ["prefect", "airflow"]):
            categories["Pipeline"].append(dep)
        elif any(x in dep.lower() for x in ["fastapi", "flask", "django", "uvicorn"]):
            categories["API"].append(dep)
        elif any(x in dep.lower() for x in ["elastic", "whoosh"]):
            categories["Search"].append(dep)
        elif any(x in dep.lower() for x in ["spacy", "transformers", "torch", "scikit"]):
            categories["NLP"].append(dep)
        elif any(x in dep.lower() for x in ["sentence-transformers", "faiss", "numpy"]):
            categories["Vector Search"].append(dep)
        elif any(x in dep.lower() for x in ["pytest", "black", "isort", "mypy"]):
            categories["Development"].append(dep)
        else:
            categories["Core"].append(dep)

    # Display non-empty categories
    for category, deps in categories.items():
        if deps:
            console.print(f"[bold cyan]{category}:[/bold cyan]")
            for dep in deps:
                console.print(f"  • {dep}")
            console.print()


def show_project_summary(config: Config, template_name: str = None):
    """Show generic project preview"""
    console.print(f"\n🎯 [bold cyan]{config.project_name} Preview[/bold cyan]")

    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Component", style="cyan bold", width=20)
    summary_table.add_column("Choice", style="white")

    summary_table.add_row("Data Sources", ", ".join(config.data_sources))
    summary_table.add_row("Storage", config.database)
    summary_table.add_row("Pipeline", config.orchestrator)
    summary_table.add_row("API Framework", config.api_framework)
    if config.search_engine:
        summary_table.add_row("Search Engine", config.search_engine)
    summary_table.add_row("Vector Search", "✅" if config.include_vector_search else "❌")
    summary_table.add_row("NLP Processing", "✅" if config.include_nlp else "❌")
    summary_table.add_row("Docker Support", "✅" if config.use_docker else "❌")

    console.print(summary_table)

def _show_success_message(config: Config, result: GenerationResult) -> None:
    """Show success message with next steps"""
    console.print(f"\n✨ [bold green]Successfully wove {config.project_name}![/bold green]")
    console.print(f"📁 Project created at: [cyan]{result.project_path}[/cyan]")

    if result.warnings:
        console.print(f"\n⚠️ [bold yellow]Warnings:[/bold yellow]")
        for warning in result.warnings:
            console.print(f"  • {warning}")

    if result.next_steps:
        console.print(f"\n🚀 [bold]Next Steps:[/bold]")
        for step in result.next_steps:
            if step.startswith("#"):
                console.print(f"  [dim]{step}[/dim]")
            else:
                console.print(f"  [cyan]{step}[/cyan]")

    # Project-specific tips
    if "pokemon" in config.project_name.lower():
        console.print(f"\n💡 [bold]Pokémon Project Tips:[/bold]")
        console.print("  • Run [cyan]python -m {}.scrapers.pokeapi_scraper[/cyan] to populate initial data".format(
            config.project_slug))
        console.print("  • Use [cyan]/search/team[/cyan] endpoint to find optimal team compositions")
        console.print("  • Check [cyan]config/pokemon_types.yaml[/cyan] for type effectiveness customization")

def _show_error_message(result: GenerationResult) -> None:
    """Show error message"""
    console.print(f"\n❌ [bold red]Project generation failed![/bold red]")
    if result.error_message:
        console.print(f"Error: {result.error_message}")


# This is the main entry point that setuptools will call
def main():
    """Main entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
