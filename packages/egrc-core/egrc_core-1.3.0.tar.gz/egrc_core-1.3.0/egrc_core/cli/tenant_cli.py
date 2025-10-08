"""
Tenant Database Management CLI for EGRC Platform.

This module provides command-line tools for managing tenant databases
including creation, deletion, migration, and monitoring.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..database.tenant_manager import get_tenant_manager
from ..logging.utils import get_logger


# Initialize CLI app
app = typer.Typer(
    name="tenant-db",
    help="Tenant Database Management CLI for EGRC Platform",
    rich_markup_mode="rich",
)

console = Console()
logger = get_logger(__name__)


@app.command()
def create(
    tenant_id: str = typer.Argument(..., help="Unique tenant identifier"),
    with_migrations: bool = typer.Option(
        True, "--migrations/--no-migrations", help="Run initial migrations"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Create a new tenant database."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Creating database for tenant: {tenant_id}", total=None
            )

            manager = get_tenant_manager()
            success = manager.create_tenant_database(tenant_id, with_migrations)

            if success:
                progress.update(
                    task,
                    description=(
                        f"✅ Successfully created database for tenant: {tenant_id}"
                    ),
                )
                console.print(
                    Panel(
                        "Tenant database created successfully!\n"
                        f"Tenant ID: {tenant_id}\n"
                        f"Database: {manager.get_tenant_database_name(tenant_id)}\n"
                        f"Migrations: {'Yes' if with_migrations else 'No'}",
                        title="Success",
                        border_style="green",
                    )
                )
            else:
                progress.update(
                    task,
                    description=f"❌ Failed to create database for tenant: {tenant_id}",
                )
                console.print(
                    Panel(
                        f"Failed to create tenant database for: {tenant_id}",
                        title="Error",
                        border_style="red",
                    )
                )
                raise typer.Exit(1)

    except Exception as e:
        console.print(
            Panel(
                f"Error creating tenant database: {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def delete(
    tenant_id: str = typer.Argument(..., help="Unique tenant identifier"),
    force: bool = typer.Option(
        False, "--force", "-", help="Force deletion without confirmation"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Delete a tenant database."""
    try:
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to delete the database for tenant "
                f"'{tenant_id}'?"
            )
            if not confirm:
                console.print("Operation cancelled.")
                raise typer.Exit(0)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Deleting database for tenant: {tenant_id}", total=None
            )

            manager = get_tenant_manager()
            success = manager.delete_tenant_database(tenant_id)

            if success:
                progress.update(
                    task,
                    description=(
                        f"✅ Successfully deleted database for tenant: {tenant_id}"
                    ),
                )
                console.print(
                    Panel(
                        "Tenant database deleted successfully!\n"
                        f"Tenant ID: {tenant_id}",
                        title="Success",
                        border_style="green",
                    )
                )
            else:
                progress.update(
                    task,
                    description=f"❌ Failed to delete database for tenant: {tenant_id}",
                )
                console.print(
                    Panel(
                        f"Failed to delete tenant database for: {tenant_id}",
                        title="Error",
                        border_style="red",
                    )
                )
                raise typer.Exit(1)

    except Exception as e:
        console.print(
            Panel(
                f"Error deleting tenant database: {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def list_tenants(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
) -> None:
    """List all tenant databases."""
    try:
        manager = get_tenant_manager()
        tenant_dbs = manager.list_tenant_databases()

        if not tenant_dbs:
            console.print(
                Panel("No tenant databases found.", title="Info", border_style="blue")
            )
            return

        # Create table
        table = Table(title="Tenant Databases")
        table.add_column("Database Name", style="cyan")
        table.add_column("Tenant ID", style="green")
        table.add_column("Size", style="yellow")
        table.add_column("Tables", style="magenta")

        for db_name in tenant_dbs:
            # Extract tenant ID from database name
            tenant_id = db_name.replace("_egrc", "")

            # Get database info
            info = manager.get_tenant_database_info(tenant_id)

            table.add_row(
                db_name,
                tenant_id,
                info.get("size", "Unknown"),
                str(info.get("table_count", 0)),
            )

        console.print(table)

    except Exception as e:
        console.print(
            Panel(
                f"Error listing tenant databases: {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def info(
    tenant_id: str = typer.Argument(..., help="Unique tenant identifier"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Get information about a tenant database."""
    try:
        manager = get_tenant_manager()
        info = manager.get_tenant_database_info(tenant_id)

        if not info.get("exists", False):
            console.print(
                Panel(
                    f"Tenant database for '{tenant_id}' does not exist.",
                    title="Not Found",
                    border_style="yellow",
                )
            )
            return

        # Create info panel
        info_text = """
Tenant ID: {info.get('tenant_id', 'N/A')}
Database Name: {info.get('database_name', 'N/A')}
Size: {info.get('size', 'Unknown')}
Table Count: {info.get('table_count', 0)}
Created At: {info.get('created_at', 'Unknown')}
        """.strip()

        console.print(
            Panel(info_text, title=f"Database Info: {tenant_id}", border_style="blue")
        )

    except Exception as e:
        console.print(
            Panel(
                f"Error getting tenant database info: {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def migrate(
    tenant_id: str = typer.Argument(..., help="Unique tenant identifier"),
    revision: str = typer.Option("head", "--revision", "-r", help="Migration revision"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run migrations for a tenant database."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Running migrations for tenant: {tenant_id}", total=None
            )

            manager = get_tenant_manager()
            success = manager.run_tenant_migrations(tenant_id)

            if success:
                progress.update(
                    task,
                    description=(
                        f"✅ Successfully ran migrations for tenant: {tenant_id}"
                    ),
                )
                console.print(
                    Panel(
                        "Migration completed successfully!\n"
                        f"Tenant ID: {tenant_id}\n"
                        f"Revision: {revision}",
                        title="Success",
                        border_style="green",
                    )
                )
            else:
                progress.update(
                    task,
                    description=f"❌ Failed to run migrations for tenant: {tenant_id}",
                )
                console.print(
                    Panel(
                        f"Failed to run migrations for tenant: {tenant_id}",
                        title="Error",
                        border_style="red",
                    )
                )
                raise typer.Exit(1)

    except Exception as e:
        console.print(
            Panel(
                f"Error running migrations: {str(e)}", title="Error", border_style="red"
            )
        )
        raise typer.Exit(1)


@app.command()
def migrate_all(
    revision: str = typer.Option("head", "--revision", "-r", help="Migration revision"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run migrations for all tenant databases."""
    try:
        manager = get_tenant_manager()
        tenant_dbs = manager.list_tenant_databases()

        if not tenant_dbs:
            console.print(
                Panel(
                    "No tenant databases found to migrate.",
                    title="Info",
                    border_style="blue",
                )
            )
            return

        console.print(f"Found {len(tenant_dbs)} tenant databases to migrate.")

        success_count = 0
        failed_tenants = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for db_name in tenant_dbs:
                tenant_id = db_name.replace("_egrc", "")
                task = progress.add_task(f"Migrating {tenant_id}", total=None)

                try:
                    success = manager.run_tenant_migrations(tenant_id)
                    if success:
                        success_count += 1
                        progress.update(task, description=f"✅ Migrated {tenant_id}")
                    else:
                        failed_tenants.append(tenant_id)
                        progress.update(task, description=f"❌ Failed {tenant_id}")
                except Exception as e:
                    failed_tenants.append(tenant_id)
                    progress.update(task, description=f"❌ Error {tenant_id}: {str(e)}")

        # Summary
        if failed_tenants:
            console.print(
                Panel(
                    "Migration completed with errors.\n"
                    f"Successful: {success_count}\n"
                    f"Failed: {len(failed_tenants)}\n"
                    f"Failed tenants: {', '.join(failed_tenants)}",
                    title="Migration Summary",
                    border_style="yellow",
                )
            )
            raise typer.Exit(1)
        else:
            console.print(
                Panel(
                    "All migrations completed successfully!\n"
                    f"Migrated {success_count} tenant databases.",
                    title="Success",
                    border_style="green",
                )
            )

    except Exception as e:
        console.print(
            Panel(
                f"Error running migrations for all tenants: {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def health_check(
    tenant_id: str | None = typer.Option(
        None, "--tenant-id", help="Check specific tenant"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Perform health check on tenant databases."""
    try:
        manager = get_tenant_manager()

        if tenant_id:
            # Check specific tenant
            info = manager.get_tenant_database_info(tenant_id)
            if info.get("exists", False):
                console.print(
                    Panel(
                        f"✅ Tenant database '{tenant_id}' is healthy\n"
                        f"Size: {info.get('size', 'Unknown')}\n"
                        f"Tables: {info.get('table_count', 0)}",
                        title="Health Check",
                        border_style="green",
                    )
                )
            else:
                console.print(
                    Panel(
                        f"❌ Tenant database '{tenant_id}' does not exist",
                        title="Health Check",
                        border_style="red",
                    )
                )
                raise typer.Exit(1)
        else:
            # Check all tenants
            tenant_dbs = manager.list_tenant_databases()

            if not tenant_dbs:
                console.print(
                    Panel(
                        "No tenant databases found.",
                        title="Health Check",
                        border_style="blue",
                    )
                )
                return

            healthy_count = 0
            unhealthy_tenants = []

            for db_name in tenant_dbs:
                tenant_id = db_name.replace("_egrc", "")
                info = manager.get_tenant_database_info(tenant_id)

                if info.get("exists", False) and not info.get("error"):
                    healthy_count += 1
                else:
                    unhealthy_tenants.append(tenant_id)

            if unhealthy_tenants:
                console.print(
                    Panel(
                        "Health check completed with issues.\n"
                        f"Healthy: {healthy_count}\n"
                        f"Unhealthy: {len(unhealthy_tenants)}\n"
                        f"Unhealthy tenants: {', '.join(unhealthy_tenants)}",
                        title="Health Check Summary",
                        border_style="yellow",
                    )
                )
                raise typer.Exit(1)
            else:
                console.print(
                    Panel(
                        "All tenant databases are healthy!\n"
                        f"Checked {healthy_count} databases.",
                        title="Health Check",
                        border_style="green",
                    )
                )

    except Exception as e:
        console.print(
            Panel(
                f"Error during health check: {str(e)}",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
