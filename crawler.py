#!/bin/env python3
import sqlite3
import leveldb
cache = leveldb.LevelDB('./url.db');

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
    contrating TEXT,
    country TEXT,
    budget TEXT
    );
    ''');


def IMDb_movie(url):
    def urlget(url):
        burl = url.encode('ascii');
        try:
            data = bytes(cache.Get(burl));
        except KeyError:
            from urllib.request import urlopen, Request
            from urllib.error import URLError
            import socket
            headers={'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0'};
            timeout = 10
            req = Request(url, headers=headers);
            while True:
                try:
                    data = urlopen(req, timeout=timeout).read();
                    break;
                except socket.timeout:
                    pass
                except URLError:
                    pass
                except KeyboardInterrupt:
                    break;
                except:
                    pass
            cache.Put(burl, data);
        finally:
            return data;
            
    while True:
        print(url);
        from bs4 import BeautifulSoup
        data = urlget(url);
        soup = BeautifulSoup(data);
                
        from urllib.parse import urljoin        
        for item in soup.select('tr[class]'):
            movie = {};
            iurl = item.select('td.title > a')[0]['href'];
            from re import match
            movie['id'] = match(r'^/title/(tt\d+)', iurl).group(1);
            movie['url'] = urljoin(url, iurl);
            data = urlget(movie['url']);
            soup0 = BeautifulSoup(data);
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

            detail = soup0.select('#maindetails_center_bottom')[0];
            movie['country'] = '';
            movie['budget'] = None;
            
            for block in detail.select('.txt-block > h4.inline'):
                if block.string == 'Country:':
                    movie['country'] = '|'.join(map(lambda foo : foo.string, block.parent.select('a[itemprop="url"]')));
                elif block.string == 'Budget:':
                    movie['budget'] = block.parent.contents[2];
            
            yield movie;

        url = urljoin(url, soup.select('span.pagination > a')[-1]['href']);

count = 10000;
for movie in IMDb_movie('http://www.imdb.com/search/title?at=0&sort=num_votes,desc'):
    print(movie);
    c.execute('''
    replace into movie
    values (:id, :url, :title, :year, :rating, :ratingcount, :genre, :duration, :contrating, :country, :budget);
    ''', movie
    );
    count -= 1;
    if count < 0:
        break;
