from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from app import app, db



if __name__ == '__main__':
  http_server = HTTPServer(WSGIContainer(app))
  http_server.listen(5000, address='0.0.0.0')
  IOLoop.instance().start()
    
