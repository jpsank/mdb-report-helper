from app import app, db, cli

cli.register(app.cli)

if __name__ == '__main__':
    app.run()
