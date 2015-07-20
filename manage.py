from flask.ext.script import Server, Manager
from werkzeug.contrib.fixers import ProxyFix

from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db

manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@localhost/mmq'
manager.add_command('db', MigrateCommand)
migrate = Migrate(app,db)
app.wsgi_app = ProxyFix(app.wsgi_app)
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()

@manager.command
def runserver():
    return
if __name__ == '__main__':
    app.run(debug=True)