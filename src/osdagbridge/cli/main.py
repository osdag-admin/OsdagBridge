import click

@click.group()
def main():
    """OsdagBridge CLI"""
    pass

@main.command()
@click.argument("model")
def validate(model):
    """Validate a bridge model JSON file."""
    print(f"Validating model: {model}")

@main.command()
def version():
    from osdagbridge import __version__
    print("OsdagBridge version:", __version__)
