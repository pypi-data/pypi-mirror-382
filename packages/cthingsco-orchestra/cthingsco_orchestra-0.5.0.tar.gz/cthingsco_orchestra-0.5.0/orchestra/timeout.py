from functools import wraps

from grpc import RpcError, StatusCode

TIMEOUT = 120


def handle_deadline(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except RpcError as error:
            if error.details().lower() == StatusCode.DEADLINE_EXCEEDED.value[1]:
                raise TimeoutError from error
            else:
                raise

    return inner
