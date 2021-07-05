import click

from app import app, db


def register(cli):
    @cli.command()
    def init():
        print("Initializing database...")
        db.create_all()

    @cli.command()
    def populate():
        from app import populate


if __name__ == '__main__':
    @click.group()
    def main_cli():
        pass
    register(main_cli)

    main_cli()
