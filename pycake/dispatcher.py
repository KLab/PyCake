import webob.exc

from pycake.controller import BaseController

import logging
logger = logging.getLogger(__name__)

from types import ModuleType
import importlib


class Dispatcher:
    """Scan controllers and dispatch to it.
    """

    #: Exception class raised when controller is not found.
    notfound_class = webob.exc.HTTPNotFound

    #: Exception class raised when find uncaught exception.
    internal_server_error_class = webob.exc.HTTPInternalServerError

    response_class = webob.Response

    def __init__(self):
        self.urlmap = {}
        self.scanned_modules = set()

    #noinspection PyBroadException
    def dispatch(self, request):
        """Dispatch `request`.

        :type request: webob.Request
        """
        try:
            controller = self.urlmap.get((request.method, request.path_info))
            if not controller:
                return self.notfound_class()
            response = controller.dispatch(request)
            if response is None:
                return self.notfound_class()
            if not callable(response):
                response = self.response_class(response)
            return response
        except webob.exc.HTTPException as e:
            logger.error("Catch HTTP exception")
            return e
        except Exception:
            logger.error("Catch uncaught exception")
            return self.internal_server_error_class()

    def scan_module(self, module):
        """Find controller in `module`.

        :param module:  module or module name to scan
        :type module:  str or ModuleType
        """
        if isinstance(module, str):
            module = importlib.import_module(module)
        module_name = module.__name__
        for name in dir(module):
            kls = getattr(module, name)
            if not isinstance(kls, type):
                continue
            if kls.__module__ is not module_name:  # ignore imported classes.
                continue
            if not issubclass(kls, BaseController):
                continue
            for method_path in kls.get_methods():
                self.urlmap[method_path] = kls

    def scan_package(self, package):
        """Scan controller classes from `package` and it's submodules.

        :param package: package to scan
        :type package: str or ModuleType
        """
        if isinstance(package, str):
            package = importlib.import_module(package)
        if not isinstance(package, ModuleType):
            raise ValueError("%s is not a package or module")

        package_name = package.__name__
        if package_name in self.scanned_modules:
            return
        self.scanned_modules.add(package_name)

        self.scan_module(package)
        for name in dir(package):
            item = getattr(package, name)
            if (isinstance(item, ModuleType) and
                    item.__name__.startswith(package_name)):
                self.scan_package(item)

    def wsgi_app(self, environ, start_response):
        request = webob.Request(environ)
        response = self.dispatch(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def run(self, host='127.0.0.1', port=8888, trace=False):
        from wsgiref.simple_server import make_server

        if trace:
            import trace as tracelib
            tracer = tracelib.Trace(timing=True,
                                    ignoremods=('logging', 're', 'sre'),
                                    )
            app = self.wsgi_app

            def tracemiddleware(env, start):
                return tracer.runfunc(app, env, start)
            self.wsgi_app = tracemiddleware

        server = make_server(host, port, self)
        server.serve_forever()
