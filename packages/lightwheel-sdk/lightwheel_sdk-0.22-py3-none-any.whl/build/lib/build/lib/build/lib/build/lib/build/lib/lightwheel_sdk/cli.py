import click
from lightwheel_sdk.loader import login_manager


@click.group()
@click.version_option()
def cli():
    """Lightwheel SDK CLI - A Python SDK for interacting with the Lightwheel API."""


@cli.command()
@click.option("--username", "-u", help="Username for login")
@click.option("--password", "-p", help="Password for login")
def login(username, password):
    """Log in to Lightwheel."""
    login_manager.login(force_login=True, username=username, password=password)
    click.echo("Successfully logged in to Lightwheel!")


@cli.command()
def logout():
    """Log out from Lightwheel."""
    login_manager.logout()
    click.echo("Successfully logged out from Lightwheel!")


def main():
    """Main entry point for the lightwheel CLI."""
    cli()


if __name__ == "__main__":
    main()
