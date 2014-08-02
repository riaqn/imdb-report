#!/bin/env python3
import sqlite3

db = sqlite3.connect('im.db', isolation_level=None);
c = db.cursor();

c.execute(
    '''create table if not exists movie (
    id TEXT PRIMARY KEY,
    url TEXT,
    title TEXT,
    year INTEGER,
    rating REAL,
    ratingcount INTEGER,
    genre TEXT,
    duration REAL,
    contrating TEXT
    );
    ''');

headers={'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0'};
timeout = 10

def IMDb_movie(url):
    from urllib.request import urlopen, Request
    while True:
        print(url);
        req = Request(url, headers=headers);
        from bs4 import BeautifulSoup
        while True:
            try:
                res = urlopen(req, timeout = timeout);
                soup = BeautifulSoup(res);
                break;
            except:
                pass
                
        from urllib.parse import urljoin        
        for item in soup.select('tr[class]'):
            movie = {};
            iurl = item.select('td.title > a')[0]['href'];
            from re import match
            movie['id'] = match(r'^/title/(tt\d+)', iurl).group(1);
            movie['url'] = urljoin(url, iurl);
            req0 = Request(movie['url'], headers = headers);
            while True:
                try:
                    res0 = urlopen(req0, timeout = timeout);
                    soup0 = BeautifulSoup(res0);
                    break;
                except:
                    pass
                    
            detail = soup0.select('div#maindetails_center_top')[0];
            overview = detail.select('div.article.title-overview')[0];
            overview_top = overview.select('td#overview-top')[0];
            movie['title'] = overview_top.select('h1.header > span.itemprop')[0].string;
            try:
                movie['year'] = int(overview_top.select('h1.header > span.nobr > a')[0].string);
            except IndexError:
                movie['year'] = None;
            try:
                movie['contrating'] = overview_top.select('div.infobar > span.titlePageSprite.absmiddle')[0]['title'];
            except IndexError:
                movie['contrating'] = None;
            try:
                duration = overview_top.select('div.infobar > time')[0].string;
                m = match(r'^\s*(\d+)\s*min\s*$', duration);
                movie['duration'] = float(m.group(1));
            except IndexError:
                movie['duration'] = None;

            movie['genre'] = '|'.join(map(lambda foo : foo.string, overview_top.select('div.infobar > a > span.itemprop')));

            try:
                movie['rating'] = float(overview_top.select('div.star-box.giga-star > div.star-box-details > strong > span')[0].string);
            except IndexError:
                movie['rating'] = None;

            try:
                movie['ratingcount'] = int(overview_top.select('div.star-box.giga-star > div.star-box-details > a > span')[0].string.replace(',', ''));
            except IndexError:
                movie['ratingcount'] = None;
            yield movie;

        url = urljoin(url, soup.select('span.pagination > a')[-1]['href']);

for movie in IMDb_movie('http://www.imdb.com/search/title?at=0&sort=num_votes'):
    print(movie);
    c.execute('''
    replace into movie
    values (:id, :url, :title, :year, :rating, :ratingcount, :genre, :duration, :contrating);
    ''', movie
    );
