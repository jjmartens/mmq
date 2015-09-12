from werkzeug.contrib.fixers import ProxyFix
from app import app, db

app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@localhost/mmq'
app.wsgi_app = ProxyFix(app.wsgi_app)
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()

if __name__ == '__main__':
    app.run(debug=True)