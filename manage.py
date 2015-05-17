from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask.ext.script import Server, Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db

manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@localhost/mmq'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600

manager.add_command('db', MigrateCommand)
migrate = Migrate(app,db)

@manager.command
def runserver():
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000, address='0.0.0.0')
    IOLoop.instance().start()

if __name__ == '__main__':
    manager.run()



