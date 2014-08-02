#!/bin/env python3
import tornado.ioloop
import tornado.web
import sqlite3

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = self.application.db;
    def get(self):
        self.write("Hello, world")

class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.db = sqlite3.connect('im.db');
        c = self.db.cursor();
        c.execute('''create table if not exists movie (
        id TEXT,
        title TEXT,
        year INTEGER,
        rating REAL,
        ratingcount INTEGER,
        duration REAL,
        contrating TEXT,
        ''');
        

application = tornado.web.Application([
    (r"/", MainHandler, ),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
