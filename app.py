from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask import Flask, render_template, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func
import json
import urllib
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

##########
# routes #
##########

@app.route('/<channel_slug>', methods=['GET', 'POST'])
def channelindex(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return "404 - Not found"
    return render_template('channelindex.html', channel=channel)

@app.route('/', methods=['GET', 'POST'])
def index():
    channels = Channel.query.all()
    return render_template('index.html', channels=channels)


@app.route('/<channel_slug>/playback', methods=['GET', 'POST'])
def broadcast(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return "404 - Not found"
    return render_template('broadcast.html', channel=channel)


@app.route('/<channel_slug>/add', methods=['POST'])
def add(channel_slug):
    data = json.loads(request.data.decode())
    id = data["id"]
    errors = []
    if len(id) != 11:
        errors.append("Add a youtube id not a link.")
        return jsonify({"error": errors})

    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return "404 - Not found"

    # see if video exists if it doesnt make a new one
    video = Video.query.filter_by(code=id).first()
    if not video:
        url = 'http://gdata.youtube.com/feeds/api/videos/{}?alt=json&v=2'.format(id)
        title_data = json.loads(urllib.urlopen(url).read())
        title = title_data['entry']['title']['$t']
        video = Video(id, title=title)
        db.session.add(video)
        db.session.commit()
    try:
        record = Record(channel.id , video.id)
        db.session.add(record)
        db.session.commit()
        return jsonify({"succes": True})
    except:
        errors.append("Unable to add item to database.")
        return jsonify({"error": errors})


@app.route('/<channel_slug>/add_existing', methods=['POST'])
def add_existing(channel_slug):
    data = json.loads(request.data.decode())
    id = data["id"]
    errors = []
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        errors.append("channel does not exist (anymore)")
        return jsonify({"error" : errors})

    # see if video exists if it doesnt make a new one
    video = Video.query.filter_by(id=id).first()
    if not video:
        errors.append("Video does not exist (anymore)")
        return jsonify({"error" : errors})
    try:
        record = Record(channel.id , video.id)
        db.session.add(record)
        db.session.commit()
        return jsonify({"succes": True})
    except:
        errors.append("Unable to add item to database.")
        return jsonify({"error": errors})

@app.route('/<channel_slug>/finish', methods=['POST'])
def finish_command(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return "404 - Not found"
    data=request.get_json()
    if 'id' not in data:
        return jsonify({'succes':False, "message" : "Geen valide post request"})

    record = Record.query.filter_by(id=data['id'],channel_id=channel.id).first()
    if not record:
        return "404 - Not found"
    record.finish()
    db.session.commit()
    return jsonify({"succes":True})



@app.route("/<channel_slug>/results", methods=['GET'])
def get_results(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return "404 - Not found"
    results = Record.query.filter_by(executed=False,channel_id=channel.id).all()
    if not results:
        random_rec = Record.query.filter_by(channel_id=channel.id).order_by(func.rand()).first()
        if random_rec:
            entry = Record(channel.id, random_rec.video.id)
            db.session.add(entry)
            db.session.commit()
            results = [entry]
    return jsonify({"videos" : map(lambda x: {'code' :x.video.code, 'r_id': x.id, 'title':x.video.title} , results)})


@app.route("/<channel_slug>/playlist", methods=['GET'])
def get_playlist(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return "404 - Not found"
    q = Record.query.filter_by(channel_id=channel.id).group_by(Record.video_id)
    results = Record.query.filter_by(executed=False,channel_id=channel.id).all()
    current = Record.query.filter_by(executed=True, channel_id=channel.id).order_by(Record.id.desc()).first()
    data = {"playlistVideos" : map(lambda x: {'code' :x.video.code,'title':x.video.title, "id":x.video.id} , q), "upcoming" : map(lambda x: {'code' :x.video.code, 'r_id': x.id, 'title':x.video.title} , results)}
    if current:
        data['current_title'] = current.video.title
    else:
        data['current_title'] = "no playback detected"
    return jsonify(data)



if __name__ == '__main__':
  http_server = HTTPServer(WSGIContainer(app))
  http_server.listen(5000, address='0.0.0.0')
  IOLoop.instance().start()

