import click


@click.group()
def api():
    pass


@api.command()
def version():
    click.echo("v3")
