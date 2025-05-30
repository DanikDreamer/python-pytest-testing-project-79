class NetworkException(Exception):
    pass


class HttpError(NetworkException):
    pass


class RequestError(NetworkException):
    pass
