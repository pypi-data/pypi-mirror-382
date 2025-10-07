import ctypes
import libusb_package

libusbpath = libusb_package.get_library_path()
try:
	_lib = ctypes.cdll.LoadLibrary(libusbpath)
except FileNotFoundError:
	if not exists(libusbpath):
		raise FileNotFoundError("libusb-1.0.so was not found on your system. Is this package correctly installed?")
	raise FileNotFoundError("libusb-1.0.so could not be loaded. There is a missing dependency.")

from ._core import __version__, Multiplexer, Channel
