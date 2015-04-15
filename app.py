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
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@localhost/mmq'
db = SQLAlchemy(app)



from models import Channel,Record,Video

###########
# utility #
###########
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        instance = model(**params)
        session.add(instance)
        return instance

# routes #
##########

@app.route('/<channel_id>/playback', methods=['GET', 'POST'])
def index(channel_id):
    channel = Channel.query.filter_by(id=channel_id).first()
    if not channel:
        return "404 - Not found"
    return render_template('index.html', channel=channel)


@app.route('/<channel>/add', methods=['POST'])
def add(channel):
    data = json.loads(request.data.decode())
    id = data["id"]
    errors = []
    if len(id) != 11:
        errors.append("Add a youtube id not a link.")
        return jsonify({"error": errors})
    # see if video exists if it doesnt make a new one
    video = Video.query.filter_by(code=id).first()
    if not video:
        video = Video(id)
        db.session.add(video)
        db.session.commit()
    try:
        record = Record(channel, video.id)
        db.session.add(record)
        db.session.commit()
        return jsonify({"succes": True})
    except:
        errors.append("Unable to add item to database.")
        return jsonify({"error": errors})

@app.route('/<channel>/finish', methods=['POST'])
def finish_command(channel):
    data=request.get_json()
    if 'id' not in data:
        return jsonify({'succes':False, "message" : "Geen valide post request"})
    video = Record.query.filter_by(id=data['id'],channel_id=channel).first()
    x.finish()
    db.session.commit()
    return jsonify({"succes":True})



@app.route("/<channel>/results", methods=['GET'])
def get_results(channel):
    results = Record.query.filter_by(executed=False,channel_id=channel).all()
    print results
    return jsonify({"videos" : map(lambda x: {'code' :x.video.code, 'id': x.id} , results)})


if __name__ == '__main__':
  http_server = HTTPServer(WSGIContainer(app))
  http_server.listen(5000, address='0.0.0.0')
  IOLoop.instance().start()

