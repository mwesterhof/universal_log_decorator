from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime

import inspect
import time


def get_wrapper_for_function(f, log_obj):
    log_obj.do_log(f, "registered for logging")

    def wrapper(*args, **kwargs):
        timestamp = datetime.now()
        log_obj.do_log(f, f"called with {len(args)} args and {len(kwargs)} kwargs ({timestamp})")

        try:
            result = f(*args, **kwargs)
        except Exception as exception:
            log_obj.do_log(f, f"raised \"{exception}\" after {datetime.now() - timestamp}")
            raise

        elapsed = datetime.now() - timestamp
        log_obj.do_log(f, f"returning after {elapsed} with result: {result}")
        return result

    wrapper._wrapped_function = f
    return wrapper
        

class LogBase:
    def __init__(self):
        self._log = defaultdict(list)

    def do_log(self, logged_obj, msg):
        self._log[logged_obj].append(msg)

    def print(self, obj=None):
        if not obj:
            funcs = [key for key in self._log.keys()]
        else:
            funcs = [obj._wrapped_function]

        for obj in funcs:
            print(f"[{obj.__name__}]")
            for line in self._log[obj]:
                print(f"\t{line}")


class FunctionLog(LogBase):
    pass


class ClassLog(LogBase):
    pass


class Logger:
    def __init__(self):
        self._function_log = FunctionLog()
        self._class_log = ClassLog()

    def _do_function_log(self, func, msg):
        self._function_log.do_log(func, msg)

    def _do_class_log(self, klass, msg):
        self._class_log.do_log(klass, msg)

    def _log_class(self, klass, methods):
        print(klass)
        print(methods)
        for method in methods:
            wrapped = get_wrapper_for_function(method, self._class_log)
            setattr(klass, method.__name__, wrapped)

    def log_class(self, klass_or_methods):
        if isinstance(klass_or_methods, Iterable):
            method_names = klass_or_methods

            def log_class_wrapped(klass):
                methods = [getattr(klass, method_name) for method_name in method_names]
                self._log_class(klass, methods)
                return klass

            return log_class_wrapped

        else:
            klass = klass_or_methods
            methods = [attr for _, attr in klass.__dict__.items() if inspect.isfunction(attr)]
            self._log_class(klass, methods)

        return klass

    def log_func(self, f):
        return get_wrapper_for_function(f, self._function_log)

    def print(self, func=None):
        self._function_log.print()
        self._class_log.print()


logger = Logger()


@logger.log_class(['foo', 'baz'])
class TestClass:
    def foo(self):
        return 1

    def bar(self):
        return self.foo() * 2

    def baz(self):
        return self.bar() * 2


tc = TestClass()
print(tc.baz())


logger.print()
