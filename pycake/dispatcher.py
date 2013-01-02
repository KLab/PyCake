import webob.exc

from . import errors
from pycake.controller import Controller

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
        self.controllers = {}
        self.scanned_modules = set()

    #noinspection PyBroadException
    def dispatch(self, request):
        try:
            path_info = request.path_info
            if path_info.count('/') < 2:  # top page
                controller_name = 'top'
                action_path = path_info
            else:
                _, controller_name, action_path = path_info.split('/', 2)
                action_path = '/' + action_path
            controller = self.controllers.get(controller_name)
            if not controller:
                return self.notfound_class()
            response = controller.dispatch(request, action_path)
            if not callable(response):
                response = self.response_class(response)
            return response
        except webob.exc.HTTPException as e:
            logger.error("Catch HTTP exception")
            return e
        except Exception as e:
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
            if not issubclass(kls, Controller):
                continue
            controller_name = name.lower()
            if controller_name in self.controllers:
                raise errors.ControllerConflict(
                    "conflict %r: %r and %r" % (
                        controller_name,
                        self.controllers[controller_name],
                        kls))
            self.controllers[name.lower()] = kls

    def scan_package(self, package):
        """Scan controller classes from `package` and it's submodules.

        :param package: package to scan
        :ptype package: str or package
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

    def run(self, host='127.0.0.1', port=8888):
        from wsgiref.simple_server import make_server
        server = make_server(host, port, self)
        server.serve_forever()
