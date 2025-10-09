# base72.py
# Implementation of Base72 encode and decode in Python 3.
#
# THE GPLv3 LICENSE
# Copyleft (©) 2025 hibays
#
'''
For example:

>>> from base72 import *

>>> b72encode(b'ABC')
b'K7g'

>>> b72encode(b'1234567890')
b'K7g0BpX5K7g'

>>> b72decode(b'K7g0BpX5K7g')
b'1234567890'
'''

__all__ = ['b72encode', 'b72decode']

_b72alphabet = b'0123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ_-+=()[]{}@,;'


def b72encode(
    data,
    len=len,
    range=range,
    bnjoin=b''.join,
    from_bytes=int.from_bytes,
    b72tab=tuple(bytes((i, )) for i in _b72alphabet)  # int → bytes
) -> bytes:
	'''Input bytes-like object, return bytes.
	This algorithm transforms 10 bytes to 13 Base72 characters.
	The encoded data is about 30% larger.
	'''
	# Precompute double-char table for performance
	b72tab2 = [bnjoin((i, j)) for i in b72tab for j in b72tab]

	datlen = len(data)
	padding = (-datlen) % 10  # bytes to pad to multiple of 10
	if padding:
		data, datlen = data + b'\0' * padding, datlen + padding

	encoded = []
	for i in range(0, datlen, 10):
		# Convert 10 bytes to big-endian integer (treat as 80-bit number)
		c = from_bytes(data[i:i + 10], 'big')

		# This is faster.
		d2_3 = c // 72
		d4_5 = d2_3 // 5184
		d6_7 = d4_5 // 5184
		d8_9 = d6_7 // 5184
		d10_11 = d8_9 // 5184

		encoded.append(bnjoin(
			(
				b72tab2[d10_11 // 5184],
				b72tab2[d10_11 % 5184],
				b72tab2[d8_9 % 5184],
				b72tab2[d6_7 % 5184],
				b72tab2[d4_5 % 5184],
				b72tab2[d2_3 % 5184],
				b72tab[c % 72]
			)
		))

	if padding:
		encoded[-1] = encoded[-1][:-padding]

	return bnjoin(encoded)


def b72decode(
    data,
    len=len,
    range=range,
    bnjoin=b''.join,
    to_bytes=int.to_bytes,
    b72nums={j: i for i,j in enumerate(_b72alphabet)}
) -> bytes:
	'''This function decodes the data that has been encoded by base72.
	Input bytes-like object, return bytes.
	'''
	datlen = len(data)
	padding = (-datlen) % 13  # chars to pad to multiple of 13
	if padding:
		data, datlen = data + b';' * padding, datlen + padding

	# To revert base72-encoded data. 13 bytes -> 10 bytes.
	# Just like a number of base 72 convert to decimal, each chunk is a number.
	result = bnjoin(
		to_bytes((((((((((((
				 b72nums[data[i    ]] # byte 13
		  * 72 + b72nums[data[i + 1]] # byte 12
		) * 72 + b72nums[data[i + 2]] # byte 11
		) * 72 + b72nums[data[i + 3]] # byte 10
		) * 72 + b72nums[data[i + 4]] # byte 9
		) * 72 + b72nums[data[i + 5]] # byte 8
		) * 72 + b72nums[data[i + 6]] # byte 7
		) * 72 + b72nums[data[i + 7]] # byte 6
		) * 72 + b72nums[data[i + 8]] # byte 5
		) * 72 + b72nums[data[i + 9]] # byte 4
		) * 72 + b72nums[data[i +10]] # byte 3
		) * 72 + b72nums[data[i +11]] # byte 2
		) * 72 + b72nums[data[i +12]] # byte 1
		, 10, 'big')
		 for i in range(0, datlen, 13)
	)

	if padding:
		result = result[:-padding]

	return result


if __name__ == '__main__':
	from os import system as osSys, name as osName
	osSys('cls' if osName in ('nt', 'dos') else 'clear')

	def c(size, depth=0, pint=('b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb')) -> str:
		if size > 1024:
			return c(size / 1024, depth + 1)
		return '%f%s' % (size, pint[depth])

	try:
		from base91 import encode as b91encode, decode as b91decode  # type: ignore
	except ImportError:
		b91encode = b91decode = lambda _: print(
		    '(No Base91 Module)', end=''
		) or b''

	from base64 import b64encode, b64decode, b85encode, b85decode
	from time import perf_counter
	from os import urandom

	data = urandom(1048575)  # 1MB random data

	def _test_mes(base, enData, norData=data):
		'''Test decode correctness and speed.'''
		t = perf_counter()
		deData = eval(f'b{base}decode')(enData)
		t = perf_counter() - t
		print(f'base{base} decoded in {t:.6f} seconds.')
		if deData == norData:
			return f'Success! Base{base}-encoded data reverted 100%.'
		from difflib import SequenceMatcher
		sim = SequenceMatcher(None, deData, norData).quick_ratio()
		return f'Failed! Only {sim*100:.9f}% match.'

	def _test_en(base, norData=data):
		t = perf_counter()
		enTest = eval(f'b{base}encode')(norData)
		t = perf_counter() - t
		print(f'base{base} encoded in {t:.6f} seconds.')
		return enTest

	# Test encoding
	en64 = _test_en(64)
	en85 = _test_en(85)
	en72 = _test_en(72)
	en91 = _test_en(91) if 'b91encode' in globals() else b''
	en94 = b''  # 如果你有 base94.py，可以加上

	lno = len(data)
	l64, l85, l72, l91 = len(en64), len(en85), len(en72), len(en91)
	la = lambda n: 100 * n / lno - 100

	print()
	print(f'normal: {c(lno)}')
	print(f'base64: {l64} ({la(l64):.2f}%)')
	print(f'base85: {l85} ({la(l85):.2f}%)')
	print(f'base72: {l72} ({la(l72):.2f}%)')
	if l91:
		print(f'base91: {l91} ({la(l91):.2f}%)')

	print()
	print(f'base64: {_test_mes(64, en64)}')
	print(f'base85: {_test_mes(85, en85)}')
	print(f'base72: {_test_mes(72, en72)}')
	if l91:
		print(f'base91: {_test_mes(91, en91)}')
