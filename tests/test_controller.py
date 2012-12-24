# -*- coding: utf-8 -*-

from _controllers import *
from webob import Request

def test_controller():
    exposed = sorted(Spam._exposed_methods.keys())
    assert exposed == [('GET', '/'), ('GET', '/spam'), ('POST', '/fizz')]

    request = Request.blank('/sapm/')
    resp = Spam.dispatch(request, '/')
    assert resp == 'Hello'

    request = Request.blank('/spam/spam')
    resp = Spam.dispatch(request, '/spam')
    assert resp == 'spam'

    request = Request.blank('/spam/fizz', POST='')
    resp = Spam.dispatch(request, '/fizz')
    assert resp == 'buzz'

    request = Request.blank('/spam/hoge')
    resp = Spam.dispatch(request, '/hoge')
    assert resp is None