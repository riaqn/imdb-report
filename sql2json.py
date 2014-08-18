import sqlite3
db = sqlite3.connect('im.db');
db.row_factory = sqlite3.Row
cur = db.execute('select * from movie;');

movies = [];
import json

convert = {};
import csv
with open('convert.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
        convert[int(row[0])] = float(row[1]);
        
def compute_budget(movie):

    budget = movie['budget'];
    year = movie['year'];
    from re import match
    m = match(r'^\s*\$\s*([\d,]+)\s*$', budget);
    if m is None:
        movie['budget'] = None;
    else:
        try:
            movie['budget'] = round(float(m.group(1).replace(',','')) / convert[year]);
        except KeyError:
            movie['budget'] = None;
        
for row in cur.fetchall():
    movie = dict(row);
    movie['genre'] = movie['genre'].split('|');
    if movie['country'] is None:
        movie['country'] = ''
    else:
        movie['country'] = movie['country'].split('|');

    if movie['budget'] is not None:
        compute_budget(movie);
    movies.append(movie);

json.dump(movies, open('movie.json', 'w'));
