#https://groups.google.com/forum/#!topic/web2py/cgSrsC73vzg
from gluon.contrib.minify import htmlmin

def minify(func):
    """
    @minify
    def some_controller():
        ...
        return dict(...)
    """
    def _f():
        out = func()
        return htmlmin.minify(response.render(out) if isinstance(out, dict) else out)
    return _f
