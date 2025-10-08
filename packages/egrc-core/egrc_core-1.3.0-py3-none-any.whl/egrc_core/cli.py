"""
Command Line Interface for EGRC Core.

This module provides CLI commands for managing the EGRC Core package.
"""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .audit import get_processor_stats, start_event_processor, stop_event_processor
from .config import Settings
from .core import get_logger
from .database import get_async_db_session


app = typer.Typer(
    name="egrc-core",
    help="EGRC Core - Governance, Risk, and Compliance Platform",
    add_completion=False,
)
console = Console()
logger = get_logger(__name__)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    console.print(
        Panel.fit(
            "[bold blue]EGRC Core[/bold blue]\n"
            f"Version: [green]{__version__}[/green]\n"
            f"Python: [yellow]{__import__('sys').version.split()[0]}[/yellow]",
            title="Version Information",
        )
    )


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    validate: bool = typer.Option(
        False, "--validate", "-v", help="Validate configuration"
    ),
    env_file: Path | None = typer.Option(
        None, "--env-file", "-e", help="Environment file path"
    ),
) -> None:
    """Manage configuration."""
    try:
        if env_file:
            settings = Settings(_env_file=env_file)
        else:
            settings = Settings()

        if show:
            _show_config(settings)

        if validate:
            _validate_config(settings)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def database(
    check: bool = typer.Option(
        False, "--check", "-c", help="Check database connection"
    ),
    migrate: bool = typer.Option(
        False, "--migrate", "-m", help="Run database migrations"
    ),
    create_tables: bool = typer.Option(
        False, "--create-tables", help="Create database tables"
    ),
) -> None:
    """Manage database operations."""
    if check:
        _check_database()
    elif migrate:
        _migrate_database()
    elif create_tables:
        _create_tables()
    else:
        console.print(
            "[yellow]No operation specified. Use --help for options.[/yellow]"
        )


@app.command()
def audit(
    start: bool = typer.Option(False, "--start", help="Start audit event processor"),
    stop: bool = typer.Option(False, "--stop", help="Stop audit event processor"),
    status: bool = typer.Option(False, "--status", help="Show audit processor status"),
    workers: int = typer.Option(
        5, "--workers", "-w", help="Number of worker processes"
    ),
) -> None:
    """Manage audit system."""
    if start:
        _start_audit_processor(workers)
    elif stop:
        _stop_audit_processor()
    elif status:
        _show_audit_status()
    else:
        console.print(
            "[yellow]No operation specified. Use --help for options.[/yellow]"
        )


@app.command()
def test(
    path: str | None = typer.Option("tests", "--path", "-p", help="Test path"),
    coverage: bool = typer.Option(False, "--coverage", "-c", help="Run with coverage"),
    parallel: bool = typer.Option(False, "--parallel", help="Run tests in parallel"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run tests."""
    import subprocess

    cmd = ["python", "-m", "pytest", path]

    if coverage:
        cmd.extend(["--cov=egrc_core", "--cov-report=html", "--cov-report=term"])

    if parallel:
        cmd.extend(["-n", "auto"])

    if verbose:
        cmd.append("-v")

    try:
        subprocess.run(cmd, check=True)
        console.print("[green]Tests completed successfully![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Tests failed with exit code {e.returncode}[/red]")
        raise typer.Exit(e.returncode)


@app.command()
def lint(
    fix: bool = typer.Option(False, "--fix", "-", help="Fix issues automatically"),
    check: bool = typer.Option(False, "--check", "-c", help="Check only, don't fix"),
) -> None:
    """Run code quality checks."""
    if fix:
        _run_lint_fix()
    elif check:
        _run_lint_check()
    else:
        _run_lint_check()


def _show_config(settings: Settings) -> None:
    """Show current configuration."""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    # Database settings
    table.add_row("Database URL", str(settings.database.url)[:50] + "...")
    table.add_row("Database Pool Size", str(settings.database.pool_size))

    # Security settings
    table.add_row("Secret Key", "***" if settings.security.secret_key else "Not set")
    table.add_row("Token Expire Minutes", str(settings.security.token_expire_minutes))

    # Logging settings
    table.add_row("Log Level", settings.logging.level)
    table.add_row("Log Format", settings.logging.format)

    console.print(table)


def _validate_config(settings: Settings) -> None:
    """Validate configuration."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Validating configuration...", total=None)

        try:
            # Validate database connection
            asyncio.run(_check_database_connection())
            progress.update(task, description="✅ Database connection valid")

            # Validate security settings
            if not settings.security.secret_key:
                raise ValueError("Secret key is required")
            progress.update(task, description="✅ Security settings valid")

            # Validate logging settings
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if settings.logging.level not in valid_levels:
                raise ValueError(f"Invalid log level: {settings.logging.level}")
            progress.update(task, description="✅ Logging settings valid")

            console.print("\n[green]✅ Configuration is valid![/green]")

        except Exception as e:
            console.print(f"\n[red]❌ Configuration validation failed: {e}[/red]")
            raise typer.Exit(1)


async def _check_database_connection() -> None:
    """Check database connection."""
    async with get_async_db_session() as session:
        await session.execute("SELECT 1")


def _check_database() -> None:
    """Check database connection."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking database connection...", total=None)

        try:
            asyncio.run(_check_database_connection())
            progress.update(task, description="✅ Database connection successful")
            console.print("\n[green]✅ Database is accessible![/green]")
        except Exception as e:
            progress.update(task, description="❌ Database connection failed")
            console.print(f"\n[red]❌ Database connection failed: {e}[/red]")
            raise typer.Exit(1)


def _migrate_database() -> None:
    """Run database migrations."""
    console.print("[yellow]Database migration not implemented yet.[/yellow]")


def _create_tables() -> None:
    """Create database tables."""
    console.print("[yellow]Table creation not implemented yet.[/yellow]")


def _start_audit_processor(workers: int) -> None:
    """Start audit event processor."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Starting audit processor...", total=None)

        try:
            asyncio.run(start_event_processor(max_workers=workers))
            progress.update(task, description="✅ Audit processor started")
            console.print(
                f"\n[green]✅ Audit processor started with {workers} workers![/green]"
            )
        except Exception as e:
            progress.update(task, description="❌ Failed to start audit processor")
            console.print(f"\n[red]❌ Failed to start audit processor: {e}[/red]")
            raise typer.Exit(1)


def _stop_audit_processor() -> None:
    """Stop audit event processor."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Stopping audit processor...", total=None)

        try:
            asyncio.run(stop_event_processor())
            progress.update(task, description="✅ Audit processor stopped")
            console.print("\n[green]✅ Audit processor stopped![/green]")
        except Exception as e:
            progress.update(task, description="❌ Failed to stop audit processor")
            console.print(f"\n[red]❌ Failed to stop audit processor: {e}[/red]")
            raise typer.Exit(1)


def _show_audit_status() -> None:
    """Show audit processor status."""
    try:
        stats = asyncio.run(get_processor_stats())

        table = Table(title="Audit Processor Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Status", "Running" if stats["is_running"] else "Stopped")
        table.add_row("Workers", str(stats["workers"]))
        table.add_row("Processed", str(stats["processed"]))
        table.add_row("Failed", str(stats["failed"]))
        table.add_row("Retried", str(stats["retried"]))

        if stats["uptime_seconds"]:
            table.add_row("Uptime", f"{stats['uptime_seconds']:.1f} seconds")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Failed to get audit status: {e}[/red]")
        raise typer.Exit(1)


def _run_lint_fix() -> None:
    """Run linting with auto-fix."""
    import subprocess

    commands = [
        ["python", "-m", "black", "egrc_core", "tests"],
        ["python", "-m", "isort", "egrc_core", "tests"],
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, check=True)
            console.print(f"[green]✅ {cmd[2]} completed successfully[/green]")
        except subprocess.CalledProcessError as e:
            console.print(
                f"[red]❌ {cmd[2]} failed with exit code {e.returncode}[/red]"
            )
            raise typer.Exit(e.returncode)


def _run_lint_check() -> None:
    """Run linting checks."""
    import subprocess

    commands = [
        ["python", "-m", "black", "--check", "egrc_core", "tests"],
        ["python", "-m", "isort", "--check-only", "egrc_core", "tests"],
        ["python", "-m", "flake8", "egrc_core", "tests"],
        ["python", "-m", "mypy", "egrc_core"],
        ["python", "-m", "pylint", "egrc_core"],
        ["python", "-m", "bandit", "-r", "egrc_core"],
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, check=True)
            console.print(f"[green]✅ {cmd[2]} passed[/green]")
        except subprocess.CalledProcessError as e:
            console.print(
                f"[red]❌ {cmd[2]} failed with exit code {e.returncode}[/red]"
            )
            raise typer.Exit(e.returncode)


def main() -> None:
    """Main entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
