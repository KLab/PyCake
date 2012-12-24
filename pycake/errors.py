class PyCakeError(Exception):
    pass


class RouteError(PyCakeError):
    pass


class ControllerConflict(PyCakeError):
    pass
