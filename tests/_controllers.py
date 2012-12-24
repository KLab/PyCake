# -*- coding: utf-8 -*-

from pycake.controller import Controller, GET, POST

class Spam(Controller):
    @GET
    def index(self):
        return "Hello"

    @GET('/spam')
    def egg(self):
        return "spam"

    @POST
    def fizz(self):
        return "buzz"

class Ham(Controller):
    @GET
    def hello(self):
        return "world"
