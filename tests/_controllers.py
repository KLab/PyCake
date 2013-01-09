# -*- coding: utf-8 -*-

from pycake.controller import BaseController, GET, POST

class Spam(BaseController):
    prefix = '/spam'

    @GET
    def index(self):
        return "Hello"

    @GET('/spam')
    def egg(self):
        return "spam"

    @POST
    def fizz(self):
        return "buzz"

class Ham(BaseController):
    @GET
    def hello(self):
        return "world"
