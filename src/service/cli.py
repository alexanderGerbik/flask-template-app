import click
from flask.cli import with_appcontext


@click.command("hello-world")
@with_appcontext
def create_task_set_command():
    click.secho("Hello world!", fg="green")


def auto_register_commands(app, module):
    for value in module.__dict__.values():
        if isinstance(value, click.Command):
            app.cli.add_command(value)
