#!/usr/bin/env python

from __future__ import print_function
import cgi
import MySQLdb
import sys
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
import yaml

class FormPage(Resource):
    def __init__(self, config):
        self.page = '<html>\n<body>\n'
        self.page = self.page + '<form method="POST">Name: <input name="name" type="text" maxlength="32"/>\n'
        self.page = self.page + 'Favorite Color: <input name="color" type="text" maxlength="32"/>\n'
        self.page = self.page + 'Cats or Dogs: <input name="animal" type="text" maxlength="32"/>\n'
        self.page = self.page + '<button type="submit" name="action" value="Submit">Submit</button></form>\n'
        self.ending_tags = '</body>\n</html>'
        self.config = config

        try:
            self.db = MySQLdb.connect(host = self.config['mysql']['host'],
                                      user = self.config['mysql']['user'],
                                      passwd = self.config['mysql']['password'],
                                      db = self.config['mysql']['db'])

        except MySQLdb.OperationalError as e:
            print("failed to connect to database")
            sys.exit(1)

        cur = self.db.cursor()
        cur.execute("SHOW TABLES LIKE 'data';")
        r = cur.fetchone()
        if not r:
            cur.execute("""CREATE TABLE data (name VARCHAR(32) UNIQUE KEY,
                        color VARCHAR(32), animal VARCHAR(32));""")
            self.db.commit()

    def render_GET(self, request):
        return self.page + self.ending_tags

    def render_POST(self, request):
        insert_query = """INSERT INTO data (name, color, animal)
                       VALUES(%s,%s,%s)"""
        try:
            cur = self.db.cursor()
            name = cgi.escape(request.args["name"][0])
            color = cgi.escape(request.args["color"][0])
            animal = cgi.escape(request.args["animal"][0])

            cur.execute(insert_query, (name, color, animal))

            self.db.commit()
        except MySQLdb.IntegrityError as e:
            return self.page + str(e.args[1]) + self.ending_tags

        return self.page + 'success' + self.ending_tags

def main():
    fstream = open("config.yml", "r")
    config = yaml.load(fstream)
    fstream.close()
    root = Resource()
    root.putChild("", FormPage(config))
    factory = Site(root)
    reactor.listenTCP(8080, factory)
    reactor.run()

main()
