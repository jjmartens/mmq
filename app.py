from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask import Flask, render_template, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
import json


#################
# configuration #
#################

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://mmq:Ypbc27T5nantKRUP@localhost/mmq'
db = SQLAlchemy(app)



from models import Video


##########
# routes #
##########

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add():
    data = json.loads(request.data.decode())
    id = data["id"]
    errors = []
    if len(id) != 11:
        errors.append("Add a youtube id not a link.")
        return jsonify({"error": errors})
    # save the results
    try:
        video = Video(id)
        db.session.add(video)
        db.session.commit()
        return str(video.id)
    except:
        errors.append("Unable to add item to database.")
        return jsonify({"error": errors})
    return jsonify({"succes": True})

@app.route('/finish', methods=['POST'])
def finish_command():
    data=request.get_json()
    if 'id' not in data:
        return jsonify({'succes':False, "message" : "Geen valide post request"})
    video = Video.query.filter_by(code=data['id']).all()
    map(lambda x: x.finish(), video)
    db.session.commit()
    return jsonify({"succes":True})



@app.route("/results", methods=['GET'])
def get_results():
    results = Video.query.filter_by(executed=False).all()
    return jsonify({"videos" : map(lambda x: {'code' :x.code, 'id': x.id} , results)})


if __name__ == '__main__':
  http_server = HTTPServer(WSGIContainer(app))
  http_server.listen(5000, address='0.0.0.0')
  IOLoop.instance().start()

