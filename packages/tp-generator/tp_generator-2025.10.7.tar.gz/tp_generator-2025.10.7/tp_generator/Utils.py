try:
	unicode # Python 2
except NameError:
	unicode = str # Python 3

import platform
import time
import uuid as _uuid
import base64
import random
import string
import binascii

if platform.python_version_tuple()[0] == "3":
	from urllib.parse import quote as urlencode, unquote as urldecode
else:
	from urllib import quote as urlencode, unquote as urldecode



def timestamp(length):
	if length <= 0:
		return 0
	elif length < 10:
		return int(time.time() / 10**(10-length))
	elif length == 10:
		return int(time.time())
	else:
		return int(time.time() * 10**(length-10))


def uuid(version):
	if version == 1:
		return str(_uuid.uuid1())
	elif version == 4:
		return str(_uuid.uuid4())


def RandomNumber(min, max):
	return random.randint(min, max)


def RandomString(length, charsets=None):
	if type(charsets) not in [str, unicode]:
		charsets = string.ascii_letters+string.digits+string.punctuation

	return "".join(random.choice(charsets) for i in range(length))


def toUTF16(message, type="LE"):
	retval = b""
	for c in message:
		if type == "LE":
			retval += binascii.unhexlify(hex(ord(c))[2:].rjust(2, "0").ljust(4, "0"))
		elif type == "BE":
			retval += binascii.unhexlify(hex(ord(c))[2:].rjust(4, "0"))
	return base64Encode(retval)


def toUTF32(message, type="LE"):
	retval = b""
	for c in message:
		if type == "LE":
			retval += binascii.unhexlify(hex(ord(c))[2:].rjust(2, "0").ljust(8, "0"))
		elif type == "BE":
			retval += binascii.unhexlify(hex(ord(c))[2:].rjust(8, "0"))
	return base64Encode(retval)


def Str2Hex(message):
	return "".join(["%02x"%ord(c) for c in message])


def Hex2Str(message):
	return "".join([chr(int(message[i:i+2], 16)) for i in range(0, len(message), 2)])


def base64Encode(message):
	if type(message) in [str, unicode]: message = message.encode("utf8")

	retval = base64.b64encode(message)
	if type(retval) in [str, unicode]:
		return retval
	return retval.decode("utf8")


def base64Decode(message):
	if type(message) in [str, unicode]: message = message.encode("utf8")

	retval = base64.b64decode(message)
	if type(retval) in [str, unicode]:
		return retval
	return retval.decode("utf8")


def base64UrlEncode(message):
	if type(message) in [str, unicode]: message = message.encode("utf8")

	retval = base64.urlsafe_b64encode(message).rstrip(b"=")
	if type(retval) in [str, unicode]:
		return retval
	return retval.decode("utf8")


def base64UrlDecode(message):
	if type(message) in [str, unicode]: message = message.encode("utf8")

	padding = b"=" * (4-(len(message)%4))
	retval = base64.urlsafe_b64decode(message+padding)
	if type(retval) in [str, unicode]:
		return retval
	return retval.decode("utf8")


def UrlEncode(message):
	return urlencode(message)


def UrlDecode(message):
	return urldecode(message)