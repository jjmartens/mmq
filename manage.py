from flask.ext.script import Server, Manager
from werkzeug.contrib.fixers import ProxyFix
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db

manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@localhost/mmq'
manager.add_command('db', MigrateCommand)
migrate = Migrate(app,db)

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()


# @manager.command
# def runserver():
#     http_server = HTTPServer(WSGIContainer(app))
#     http_server.listen(5000, address='0.0.0.0')
#     IOLoop.instance().start()

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run()
