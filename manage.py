from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
import os

from app import app, db

migrate = Migrate(app, db)
manager = Manager(app)


if __name__ == '__main__':
    manager.run()
