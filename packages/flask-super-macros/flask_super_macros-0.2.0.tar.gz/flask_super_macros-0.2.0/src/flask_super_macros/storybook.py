from flask import Blueprint, current_app, request, abort
import os
import click


storybook_bp = Blueprint("storybook", __name__, url_prefix="/__storybook")


@storybook_bp.route("/<macro_name>")
def index(macro_name):
    macro = current_app.jinja_env.macros.get(macro_name)
    if not macro:
        abort(404)
    kwargs = request.args.to_dict()
    caller = kwargs.pop("caller", None)
    if caller:
        kwargs['caller'] = lambda: caller
    return macro(**kwargs), {"Access-Control-Allow-Origin": "*"}


@click.command()
@click.option('--port', default=6600, help='Port to run the storybook server on')
def main(port):
    from flask import Flask
    from . import SuperMacros

    app = Flask(__name__, root_path=os.getcwd())
    SuperMacros(app, macros_folder=".", register_from_env=False, storybook=True)

    click.echo(f"Found {len(app.macros.macros)} macros")
    if app.macros.macros:
        click.echo(", ".join(app.macros.macros.keys()))

    @app.route("/")
    def index():
        return "Run storybook using server renderer"

    app.run(debug=True, port=port)


if __name__ == "__main__":
    main()