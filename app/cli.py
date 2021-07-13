import click
import os


def register(cli):
    @cli.command()
    def init():
        print("Initializing database...")
        os.system("flask db init")
        os.system("flask db migrate")
        os.system("flask db upgrade")


if __name__ == '__main__':
    @click.group()
    def main_cli():
        pass
    register(main_cli)

    main_cli()
