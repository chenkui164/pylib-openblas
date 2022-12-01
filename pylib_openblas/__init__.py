import os
import sys

__dir__ = os.path.dirname(__file__)
library_dir = os.path.join(__dir__, 'lib')

if sys.platform == "win32":
    static_library = "libopenblas.lib"
    include_dir = os.path.join(__dir__, 'include')
else:
    static_library = "libopenblas.a"
    include_dir = os.path.join(__dir__, 'include', 'openblas')
