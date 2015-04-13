from app import db

class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String())
    executed = db.Column(db.Boolean)

    def finish(self):
        self.executed = True

    def __init__(self, code):
        self.code = code
        self.executed = False

    def __repr__(self):
        return '<id {}>'.format(self.id)