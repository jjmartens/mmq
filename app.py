from flask import Flask, render_template, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func
import time
import json
import random
#################
# configuration #
#################
if __name__ == '__main__':
    print "This is not how you should run this application. "
    print "Try python manage.py runserver"
    exit()

app = Flask(__name__)
db = SQLAlchemy(app)

from models import Channel, Record, Video

##########
# routes #
##########
@app.route('/<channel_slug>', methods=['GET', 'POST'])
def channelindex(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return jsonify({"msg","notfound"})
    records = db.session.query(func.count(Record.id).label('aantal'), Video.code.label('code'), Video.title.label('title'), Video.duration.label('duration')).filter(Record.channel_id==channel.id).join(Video).group_by(Video.id).all()
    return render_template('channelindex.html', channel=channel, records=records)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/channels', methods=['GET', 'POST'])
def channels():
    channels = Channel.query.all()
    return jsonify({"channels" : map(lambda x: {'title' :x.title, 'slug': x.slug} , channels)})

@app.route('/add', methods=['POST'])
def addchannel():
    data = json.loads(request.data)
    title = data["title"]
    errors = {}
    try:
        channel = Channel(title)
        db.session.add(channel)
        db.session.commit()
        return jsonify({"succes": True})
    except:
        errors.append("Unable to add channel to database.")
        return jsonify({"error": errors})

@app.route('/<channel_slug>/add', methods=['POST'])
def add(channel_slug):
    data = json.loads(request.data)
    id = data["id"]
    errors = []
    if len(id) != 11:
        errors.append("Add a youtube id not a link.")
        return jsonify({"error": errors})

    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return jsonify({"msg","notfound"})

    # see if video exists if it doesnt make a new one
    video = Video.query.filter_by(code=id).first()
    if not video:
        title = data["title"]
        duration = data["duration"]
        video = Video(id, title=title,duration=duration)
        db.session.add(video)
        db.session.commit()
    try:
        record = Record(channel.id , video.id)
        channel.update_id = channel.update_id + 1
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
        return jsonify({"msg","notfound"})
    data=request.get_json()
    if 'id' not in data:
        return jsonify({'succes':False, "message" : "Geen valide post request"})

    record = Record.query.filter_by(id=data['id'],channel_id=channel.id).first()
    if not record:
        return "404 - Not found"
    channel.update_id = channel.update_id + 1
    record.finish()
    db.session.commit()
    return jsonify({"succes":True})

@app.route('/<channel_slug>/remove', methods=['POST'])
def remove_command(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return jsonify({"msg","notfound"})
    data=request.get_json()
    if 'id' not in data:
        return jsonify({'succes':False, "message" : "Geen valide post request"})
    record = Record.query.filter_by(id=data['id'],channel_id=channel.id).first()
    channel.update_id = channel.update_id + 1
    db.session.delete(record)
    db.session.commit()
    return jsonify({"succes":True})

@app.route("/<channel_slug>/set/volume", methods=['POST'])
def set_volume(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return jsonify({"msg","notfound"})
    data=request.get_json()
    if 'vol' not in data:
        return jsonify({'succes':False, "message" : "Geen valide post request"})
    if int(data['vol']) > 0 and int(data['vol']) < 101:
        channel.update_id = channel.update_id + 1
        channel.volume = int(data['vol'])
        db.session.commit()
    return jsonify({"succes":True})

@app.route("/<channel_slug>/send/update", methods=['POST', 'GET'])
def send_update(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return jsonify({'fail':'Channel not found'})
    if channel.update == 0:
        channel.update = 1
        channel.update_id += 1
        db.session.commit()
        return jsonify({'succes':"Doot doot"})
    return jsonify({'failed':'doot doot not allowed :(. To unlock this feature send me an email.'})
    
@app.route("/<channel_slug>/ack/update", methods=['POST', 'GET'])
def received_update(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    if not channel:
        return jsonify({'fail':'Channel not found'})
    if channel.update == 1:
        channel.update = 0
        db.session.commit()
        return jsonify({'succes':'einde doot doot'})
    return jsonify({'failed':'doot doots are blocked :(. To unlock this feature send me an email.'})
@app.route("/<channel_slug>/playlist", methods=['POST'])
def get_playlist(channel_slug):
    channel = Channel.query.filter_by(slug=channel_slug).first()
    postdata = request.get_json()
    if not channel:
        return jsonify({"error" : "404 - Not found"})
    for i in range(1000):
        if 'update_id' in postdata and postdata['update_id'] < channel.update_id:
            q = Record.query.filter_by(channel_id=channel.id, executed=True).order_by(Record.id.desc()).limit(20)
            results = Record.query.filter_by(executed=False,channel_id=channel.id).all()
            if not results:
                random_rec_q = Record.query.filter_by(channel_id=channel.id)
                rand = random.randrange(0, random_rec_q.count())
                random_rec = random_rec_q.all()[rand]
                if random_rec:
                    entry = Record(channel.id, random_rec.video.id)
                    channel.update_id += 1
                    db.session.add(entry)
                    db.session.commit()
                    results = [entry]
            current = Record.query.filter_by(executed=True, channel_id=channel.id).order_by(Record.id.desc()).first()
            data = {
                "playlistVideos" : map(lambda x: {'code' :x.video.code,'title':x.video.title, "id":x.video.id} , q),
                "upcoming" : map(lambda x: {'code' :x.video.code, 'r_id': x.id, 'title':x.video.title, 'duration': x.video.duration} , results),
                "volume" : channel.volume,
                "update_id" : channel.update_id,
                "update" : channel.update
            }
            if current:
                data['current_title'] = current.video.title
            else:
                data['current_title'] = "no playback detected"
            return jsonify(data)
        db.session.commit()
        channel = Channel.query.filter_by(slug=channel_slug).first()
        time.sleep(0.05)
    return jsonify({'update_id':channel.update_id})


