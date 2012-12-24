# -*- coding: utf-8 -*-

from _controllers import *
from pycake.dispatcher import Dispatcher
from webob import Request


def test_dispatcher():
    dispatcher = Dispatcher()
    dispatcher.scan_module('_controllers')
    assert dispatcher.controllers.keys() == {'spam', 'ham'}

    request = Request.blank('/spam/')
    response = dispatcher.dispatch(request)
    assert response.text == 'Hello'
    assert response.charset == 'UTF-8'