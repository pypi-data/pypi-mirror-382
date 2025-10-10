"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Clesyde_Cloud_Lib."""


if __name__ == "__main__":
    main(prog_name="clesyde_cloud_lib")  # pragma: no cover
