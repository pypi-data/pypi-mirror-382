#!/usr/bin/env python
import sys
import click
from .context import Context
from .clean_click import CleanGroup

def app_close(msg=None):
    if msg:
        print(msg)
    context.close()
    sys.exit(0)

@click.group(cls=CleanGroup, invoke_without_command=True)
@click.pass_context
def main(ctx):
    global context
    context = Context()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        app_close()

@main.group(cls=CleanGroup)
def models():
    pass

@models.command()
def list():
    """List available models"""
    models = context.get_models()
    if models:
        print(f"{'Name':<32}{'Provider':<16}Settings")
        for model in models:
            print(f"{model['model_name']:<32}{model['provider']:<16}{model['settings']}")
    app_close()

@models.command()
@click.argument("model_name")
@click.argument("provider")
@click.argument("settings")
def add(model_name, provider, settings):
    """Add a model"""
    context.add_model(model_name, provider, settings)
    app_close("Done.")

@models.command()
@click.argument("model_name")
def delete(model_name):
    """Delete a model"""
    context.del_model(model_name)
    app_close("Done.")

@models.command()
def get():
    """Get active model"""
    model = context.get_active_model()
    print(f"Active model: {model}")
    app_close()

@models.command()
@click.argument("model_name")
def set(model_name):
    """Set active model"""
    context.set_active_model(model_name)
    app_close("Done.")

@main.command()
def prompt():
    """Enter prompt"""
    print("Press ctrl-d to finish.")
    prompt = sys.stdin.read()
    response = context.prompt(prompt)
    print(f"Response:\n{response}")
    app_close()

@main.command()
def reset():
    """Reset current context"""
    context.reset()
    app_close("Done.")

if __name__ == "__main__":
    main()