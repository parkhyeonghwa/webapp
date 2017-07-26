#!/usr/bin/env python

from __future__ import print_function
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

import cgi
import yaml

class FormPage(Resource):
    def __init__(self, config):
        self.page = '<html>\n<body>\n'
        self.page = self.page + '<form method="POST">Name: <input name="name" type="text" /></form>\n'
        self.page = self.page + '<form method="POST">Favorite Color: <input name="color" type="text" /></form>\n'
        self.page = self.page + '<form method="POST">Cats or Dogs: <input name="animal" type="text" /></form>\n'
        self.ending_tags = '</body>\n</html>'
        self.config = config

    def render_GET(self, request):
        print(request)
        return self.page + self.ending_tags

    def render_POST(self, request):
        print(request)
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
