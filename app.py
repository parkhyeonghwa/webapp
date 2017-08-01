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
        # prepare the html for the site
        self.page = '<html>\n<body>'
        self.page = self.page + '<form method="POST"><label>Name: </label><input name="name" type="text" maxlength="32"/><br>'
        self.page = self.page + '<label>Favorite Color: </label><input name="color" type="text" maxlength="32"/><br>'
        self.page = self.page + '<label>Cats or Dogs: </label><input name="animal" type="text" maxlength="32"/><br>'
        self.page = self.page + '<button type="submit" name="action" value="Submit">Submit</button></form>'
        self.ending_tags = '</body></html>'
        self.config = config

        # connect to the mysql db
        try:
            self.db = MySQLdb.connect(host = self.config['mysql']['host'],
                                      user = self.config['mysql']['user'],
                                      passwd = self.config['mysql']['password'],
                                      db = self.config['mysql']['db'])

        # Quit if you fail to connect to the db
        except MySQLdb.OperationalError as e:
            print("failed to connect to database")
            sys.exit(1)

        # Create the table for the db if it does not exist
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
        # Collect data from the form and put it in the databse
        insert_query = """INSERT INTO data (name, color, animal)
                       VALUES(%s,%s,%s)"""
        try:
            cur = self.db.cursor()
            name = cgi.escape(request.args["name"][0])
            color = cgi.escape(request.args["color"][0])
            animal = cgi.escape(request.args["animal"][0])

            cur.execute(insert_query, (name, color, animal))

            self.db.commit()

        # If the data insert fails, return that it failed and the reason why
        except MySQLdb.IntegrityError as e:
            return self.page + str(e.args[1]) + self.ending_tags

        # If we succeed, inform the user
        return self.page + 'success' + self.ending_tags

def main():
    # Open the config file and grab the configuration
    fstream = open("config.yml", "r")
    config = yaml.load(fstream)
    fstream.close()

    # Create the site and start the server
    root = Resource()
    root.putChild("", FormPage(config))
    factory = Site(root)
    reactor.listenTCP(8080, factory)
    reactor.run()

main()
