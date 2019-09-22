from datetime import date
from urllib import request

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
    connected_date = db.Column(db.DateTime)
    last_update = db.Column(db.DateTime, onupdate=date.today())
    current = db.Column(db.Integer, default=1)
    albums = db.relationship('Album', secondary=albums,
                             backref=db.backref('user', lazy='joined'))

    def __repr__(self):
        return self.name

    def favourite_list(self):
        string = 'Избранное:\n'
        for item, album in enumerate(self.albums):
            string += '{}. {}\n'.format(item + 1, album.name)
        return 'Список \'Избранное\' пуст!' if not self.albums else string

    def next(self):
        if Album.query.count() > self.current:
            self.current += 1
            db.session.commit()

    def prev(self):
        if self.current > 1:
            self.current -= 1
            db.session.commit()


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    genre = db.Column(db.String(32))
    country = db.Column(db.String(32))
    date = db.Column(db.Date)
    image = db.Column(db.String(128))
    download_link = db.Column(db.String(128))
    song_list = db.Column(db.String(256))
    info = db.Column(db.String(64))

    def __init__(self, args):
        self.name = args['name'] or 'Empty'
        self.genre = args['genre'] or 'Empty'
        self.country = args['country'] or 'Empty'
        self.download_link = args['download'] or 'Empty'
        self.image = args['img'] or 'Empty'
        self.song_list = args.song_str() or 'Empty'
        self.date = args['date']
        self.info = args['info']

    def __str__(self):
        date_format = self.date.strftime('%Y %B %d') or 'Empty'
        return '*{}*\n\nGenre: {}\n' \
               'Country: {}\nRelease date: {}\n\n' \
               'Song list:\n{}'.format(self.name, self.genre, self.country,
                                       date_format, self.song_list)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other

    def load_img(self):
        try:
            img_dir = 'utils/logo.png'
            file = open(img_dir, 'wb')
            file.write(request.urlopen(self.image).read())
            file.close()
        except Exception as e:
            img_dir = 'utils/default.png'
        return img_dir
