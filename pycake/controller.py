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


def _scan_methods(cls):
    exposed = {}
    for name in dir(cls):
        obj = getattr(cls, name)
        if not callable(obj):
            continue
        method = getattr(obj, '_method', None)
        route = getattr(obj, '_route', None)
        if method and route:
            exposed[(method, cls.prefix + route)] = obj
    return exposed


class BaseController:

    #: scanned exposed methods.
    #: {(http method in string, path): method callable}
    exposed_methods = None

    #: specify prefix explicitly
    #: This should be match with "(/\w+)+".
    prefix = ''

    def __init__(self, request):
        self.request = request

    def before_request(self):
        pass

    def after_request(self, response):
        return response

    @classmethod
    def get_methods(cls):
        if cls.exposed_methods is None:
            cls.exposed_methods = _scan_methods(cls)
        return cls.exposed_methods

    @classmethod
    def dispatch(cls, request):
        """Dispatch request and returns response.

        :param webob.Request request: request object.
        """
        method = cls.get_methods().get((request.method, request.path_info))
        if method is None:
            return None

        self = cls(request)
        response = self.before_request()
        if response:
            return response
        response = method(self)
        return self.after_request(response)
