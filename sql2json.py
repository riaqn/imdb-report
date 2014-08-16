import sqlite3
db = sqlite3.connect('im.db');
db.row_factory = sqlite3.Row
cur = db.execute('select * from movie;');

movies = [];
import json
for row in cur.fetchall():
    movie = dict(row);
    movie['genre'] = movie['genre'].split('|');
    if movie['country'] is None:
        movie['country'] = ''
    else:
        movie['country'] = movie['country'].split('|');
    movies.append(movie);

json.dump(movies, open('movie.json', 'w'));
