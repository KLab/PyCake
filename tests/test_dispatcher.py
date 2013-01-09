# -*- coding: utf-8 -*-

from pycake.dispatcher import Dispatcher
from webob import Request


def test_dispatcher():
    dispatcher = Dispatcher()
    dispatcher.scan_module('_controllers')
    assert ('GET', '/spam/') in dispatcher.urlmap

    request = Request.blank('/spam/')
    response = dispatcher.dispatch(request)
    assert response.text == 'Hello'
    assert response.charset == 'UTF-8'