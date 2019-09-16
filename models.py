from datetime import date

from app import db

albums = db.Table('user_albums',
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                  db.Column('album_id', db.Integer, db.ForeignKey('album.id'))
                  )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, unique=True)
    username = db.Column(db.String(128), unique=True)
    name = db.Column(db.String(128), unique=True)
    last_update = db.Column(db.DateTime, onupdate=date.today())
    albums = db.relationship('Album', secondary=albums,
                             backref=db.backref('user', lazy='joined'))

    def __repr__(self):
        return self.name

    def favourite_list(self):
        string = 'Избранное:\n'
        num = 1
        for i in self.albums:
            string += '{}. {}\n'.format(num, i.name)
            i += 1
        return 'Список \'Избранное\' пуст!' if not self.albums else string


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    genre = db.Column(db.String(32))
    country = db.Column(db.String(32))
    date = db.Column(db.Date)
    image = db.Column(db.String(256))
    download_link = db.Column(db.String(256))
    song_list = db.Column(db.String(256))

    def __init__(self, args):
        self.name = args.get('name') or 'None'
        self.genre = args.get('genre') or 'None'
        self.country = args.get('country') or 'None'
        self.download_link = args.get('download') or 'None'
        self.image = args.get('img') or 'None'
        self.song_list = args.song_str()
        self.date = args.get('date')

    def __str__(self):
        return '*{}*\n\nGenre: {}\n' \
               'Country: {}\nRelease date: {}\n\n' \
               'Song list:\n{}'.format(self.name, self.genre, self.country,
                                       self.date, self.song_list)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other