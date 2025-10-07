"""small timer function"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import time


def timing(function):
    """lazy method to time my function"""

    def wrap(*args, **kw):
        """wrap the function to time it"""
        time1 = time.time()
        ret = function(*args, **kw)
        time2 = time.time()
        print(f"----- {function.func_name} took {(time2 - time1):0.3f} s")
        return ret

    return wrap
