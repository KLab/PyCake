import sys
import webob.exc

from . import errors
from pycake.controller import Controller

import logging
logger = logging.getLogger(__name__)


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

    def scan_module(self, module_name):
        """Find controller in `module_name` module.
        """
        mod = sys.modules[module_name]
        for name in dir(mod):
            kls = getattr(mod, name)
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

    def scan_package(self, package_name):
        """Scan modules in a package `package_name`.

        Scanning is done by looking `sys.modules`.
        You should import modules before using `scan_package`
        """
        for module_name in sys.modules.keys():
            if module_name.startswith(package_name + '.'):
                self.scan_module(module_name)

    def wsgi_app(self, environ, start_response):
        request = webob.Request(environ)
        response = self.dispatch(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
