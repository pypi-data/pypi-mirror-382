__all__ = [
    'b94encode', 'b94decode', 'rs_b94encode', 'rs_b94decode', 'py_b94encode',
    'py_b94decode', 'b72encode', 'b72decode', 'rs_b72encode', 'rs_b72decode',
    'py_b72encode', 'py_b72decode'
]

from .base94 import b94encode as py_b94encode, b94decode as py_b94decode

try:
	from ._base94 import b94encode, b94decode  # type: ignore
	rs_b94encode, rs_b94decode = b94encode, b94decode
except ImportError:
	rs_b94encode, rs_b94decode = None, None

b94encode = py_b94encode if rs_b94encode is None else rs_b94encode

b94decode = py_b94decode if rs_b94decode is None else rs_b94decode

from .base72 import b72encode as py_b72encode, b72decode as py_b72decode

try:
	from ._base94 import b72encode, b72decode  # type: ignore
	rs_b72encode, rs_b72decode = b72encode, b72decode
except ImportError:
	rs_b72encode, rs_b72decode = None, None

b72encode = py_b72encode if rs_b72encode is None else rs_b72encode

b72decode = py_b72decode if rs_b72decode is None else rs_b72decode
