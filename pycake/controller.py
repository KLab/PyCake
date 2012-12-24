# -*- coding: utf-8 -*-

from .errors import RouteError


def _set_route(func, method, route=None):
    if route is None:
        if func.__name__ == 'index':
            route = '/'
        else:
            route = '/' + func.__name__
    else:
        if route[0] != '/':
            raise RouteError("Route should be starts with '/': %r" % (route,))
    func._method = method
    func._route = route


def GET(arg):
    """Decorator for view method.

    Can be used as decorator or decorator factory. ::

        class SpamController(Controller):

            @GET # routed to '/'
            def index(self):
                return "<a href="/hello/world">hello</a>"

            @GET('/hello/<msg:str>')
            def hello(self, msg):
                return "Hello, " + msg
    """
    if callable(arg):
        _set_route(arg, 'GET')
        return arg

    def decorator(func):
        _set_route(func, 'GET', arg)
        return func
    return decorator


def POST(arg):
    """Works like `GET` but routed to POST method."""
    if callable(arg):
        _set_route(arg, 'POST')
        return arg

    def decorator(func):
        _set_route(func, 'POST', arg)
        return func
    return decorator


class _ControllerMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        klass = type.__new__(cls, name, bases, namespace, **kwds)
        klass._exposed_methods = exposed = {}
        for name, obj in namespace.items():
            if not callable(obj):
                continue
            method = getattr(obj, '_method', None)
            route = getattr(obj, '_route', None)
            if method and route:
                exposed[(method, route)] = obj
        return klass


class Controller(metaclass=_ControllerMeta):

    #: scanned exposed methods. (generated by metaclass)
    _exposed_methods = {}

    def __init__(self, request, action_path):
        self.request = request
        self.action_path = action_path

    def before_request(self):
        pass

    def after_request(self, response):
        return response

    @classmethod
    def dispatch(cls, request, action_path):
        """Dispatch request and returns response.

        :param request: request object.
        :type request: webob.Request.
        """
        method = cls._exposed_methods.get((request.method, action_path))
        if method is None:
            return None

        self = cls(request, action_path)
        response = self.before_request()
        if response:
            return response
        response = method(self)
        return self.after_request(response)