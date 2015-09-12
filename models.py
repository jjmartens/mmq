from app import db
from slugify import slugify


class Record(db.Model):
    __tablename__ = 'record'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    executed = db.Column(db.Boolean)
    def __init__(self, channel,video):
        self.channel_id = channel
        self.video_id = video
        self.executed = False

    def __repr__(self):
        return '<id:{}, video:{}, channel:{}>'.format(self. id,self. video_id,self. channel.id)

    def finish(self):
        self.executed = True




class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer , primary_key=True)
    code = db.Column(db.String(11))
    title = db.Column(db.String(64))
    duration = db.Column(db.Integer())
    records = db.relationship('Record', backref='video',
                                lazy='dynamic')

    def __init__(self, code, title="Darude - Sandstorm", duration=260):
        self.duration = duration
        self.code = code
        self.title = title
        self.executed = False

    def __repr__(self):
        return '<id:{} ,title {}, code {}>'.format(self.id, self.title, self.code)

class Channel(db.Model):
    __tablename__ = 'channel'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    records = db.relationship('Record', backref='channel',
                            lazy='dynamic')
    slug = db.Column(db.String(64))
    volume = db.Column(db.Integer)
    update_id = db.Column(db.Integer)
    update = db.Column(db.Integer)

    def __init__(self,title):
        self.title = title
        self.slug = slugify(title)
        self.volume = 50
        self.update_id = 0
        self.update = 0


