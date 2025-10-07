from functools import wraps
from types import MethodType

def furthr_wrap(force_list=False):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kws):
            response = function(*args, **kws)
            data = None
            if response.status_code in [200, 400, 401, 403, 500]:
                data = response.json()
            
            if response.status_code != 200:
                print("error", response.status_code)
                if data is not None:
                    print("message", data["message"])
                else:
                    raise ValueError("Server returned an error")

            if data["status"] == "error":
                print("error", data["message"])
                return
            else:
                if force_list:
                    return data["results"]
                if len(data["results"]) == 1:
                    return data["results"][0]
                else:
                    return data["results"]
        return wrapper
    return decorator

def instance_overload(self, methods):
    """ Adds instance overloads for one or more classmethods"""
    for name in methods:
        if hasattr(self, name):
            setattr(self, name, MethodType(getattr(self, name).__func__, self))
