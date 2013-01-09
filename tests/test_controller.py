# -*- coding: utf-8 -*-

from _controllers import *
from webob import Request

def test_controller():
    methods = Spam.get_methods()
    assert methods.keys() == {('GET', '/spam/'), ('GET', '/spam/spam'), ('POST', '/spam/fizz')}

    request = Request.blank('/spam/')
    resp = Spam.dispatch(request)
    assert resp == 'Hello'

    request = Request.blank('/spam/spam')
    resp = Spam.dispatch(request)
    assert resp == 'spam'

    request = Request.blank('/spam/fizz', POST='')
    resp = Spam.dispatch(request)
    assert resp == 'buzz'

    request = Request.blank('/spam/hoge')
    resp = Spam.dispatch(request)
    assert resp is None