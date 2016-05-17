#https://groups.google.com/forum/#!topic/web2py/cgSrsC73vzg
from gluon.contrib.minify import htmlmin
from gluon import current

"""
Beware! Given from gluon import current, it is correct to use current.request and any of the other thread local objects but one should never assign them to global variables in the module, such as in
request = current.request # WRONG! DANGER!
nor should one use current to assign class attributes:
class MyClass:
    request = current.request # WRONG! DANGER!
This is because the thread local object must be extracted at runtime. Global variables instead are defined only once when the model is imported for the first time.
"""

def minify(func):
    """
    @minify
    def some_controller():
        ...
        return dict(...)
    """
    def _f():
        out = func()
        return htmlmin.minify(current.response.render(out) if isinstance(out, dict) else out)
    return _f
