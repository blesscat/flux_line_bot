
from collections import deque
from threading import Semaphore
from struct import Struct
from errno import ETIMEDOUT
import logging
import msgpack

import usb.core
import usb.util

from fluxclient import __version__

logger = logging.getLogger(__name__)
HEAD_PACKER = Struct("<HB")
ID_VENDOR = 0xffff
ID_PRODUCT = 0xfd00


def match_direction(direction):
    def wrapper(ep):
        return usb.util.endpoint_direction(ep.bEndpointAddress) == direction
    return wrapper


class USBProtocol(object):
    running = False
    _buf = b""

    def __init__(self):
        devices = list(usb.core.find(idVendor=ID_VENDOR, idProduct=ID_PRODUCT,
                                     find_all=True))
        devices.sort(key=lambda d: d.address)
        if len(devices) == 0:
            raise FluxUSBError("FLUX Device not found")
        elif len(devices) > 1:
            raise FluxUSBError("More then 1 FLUX Device found")

        self._usbdev = dev = devices[-1]
        logger.debug("USB device found")
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)

        dev.set_configuration()
        cfg = dev.get_active_configuration()
        intf = cfg[(0, 0)]

        self._rx = usb.util.find_descriptor(
            intf, bmAttributes=0x2,
            custom_match=match_direction(usb.util.ENDPOINT_IN))

        self._tx = usb.util.find_descriptor(
            intf, bmAttributes=0x2,
            custom_match=match_direction(usb.util.ENDPOINT_OUT))
        logger.debug("USB TX/RX confirmed")
        self.do_handshake()
        self.chl_semaphore = Semaphore(0)
        self.channels = {}

    def _send(self, buf):
        # Low level send
        try:
            self._tx.write(buf)
        except usb.core.USBError as e:
            if e.errno == ETIMEDOUT:
                raise FluxUSBError("USB operation timeout")
            else:
                raise FluxUSBError("USB io error: %s" % e)

    def _send_binary_ack(self, channel_idx):
        self._send(HEAD_PACKER.pack(4, channel_idx) + b"\x80")

    def _recv(self, length, timeout=0.001):
        # Low level recv
        try:
            # note: thread will dead lock if tiemout is 0
            return self._rx.read(length, int(timeout * 1000)).tobytes()
        except usb.core.USBError as e:
            if e.errno == ETIMEDOUT:
                return b""
            else:
                raise FluxUSBError("USB io error: %s" % e)

    def _feed_buffer(self, timeout=0.05):
        self._buf += self._recv(1024, timeout=0.05)

    def _unpack_buffer(self):
        l = len(self._buf)
        if l > 3:
            size, channel_idx = HEAD_PACKER.unpack(self._buf[:3])
            if size > 1024:
                raise FluxUSBError("Bad payload size")
            if size == 0:
                self._buf = self._buf[2:]
                return -1, None, None
            if l >= size:
                fin = self._buf[size - 1]
                buf = self._buf[3:size - 1]
                self._buf = self._buf[size:]
                return channel_idx, buf, fin
        return None, None, None

    def _begin_handshake(self):
        data = None
        self._feed_buffer(timeout=0.1)

        while True:
            d = self._unpack_buffer()
            if d[0] is None:
                break
            else:
                data = d

        if data is not None:
            channel_idx, buf, fin = data
            if channel_idx != 0xff or fin != 0xfe:
                return False

            data = msgpack.unpackb(buf, use_list=False, encoding="utf8",
                                   unicode_errors="ignore")
            self.session = data["session"]
            logger.debug("Get handshake session: %s", self.session)
            self.send_object(0xff, {"session": self.session,
                                    "client": "fluxclient-%s" % __version__})
            return True
        else:
            return False

    def _complete_handshake(self):
        self._feed_buffer(timeout=0.05)
        channel_idx, buf, fin = self._unpack_buffer()
        if channel_idx == 0xfe and fin == 0xfe:
            data = msgpack.unpackb(buf, use_list=False, encoding="utf8",
                                   unicode_errors="ignore")
            if data["session"] == self.session:
                logger.debug("USB handshake completed")
                return True
            else:
                logger.debug("Recv handshake session: %s", data["session"])
                logger.debug("Handshake failed")
                return False

        if channel_idx is not None:
            logger.debug("USB handshake response wrong channel: 0x%02x",
                         channel_idx)
            return False

        logger.debug("USB handshake response timeout")
        return False

    def do_handshake(self):
        ttl = 3
        while not self._begin_handshake():
            if ttl:
                logger.debug("Handshake timeout, retry")
                ttl -= 1
            else:
                raise FluxUSBError(ETIMEDOUT, "Timeout")
            self.send_object(0xfd, None)
            logger.debug("Handshake message not recived, retry.")
        if self._complete_handshake() is False:
            logger.debug("Handshake response error, retry.")
            self.do_handshake()

    def run_once(self):
        self._feed_buffer()
        channel_idx, buf, fin = self._unpack_buffer()
        if channel_idx is None:
            return
        elif channel_idx == -1:
            raise FluxUSBError("USB protocol broken")
        elif channel_idx < 0x80:
            channel = self.channels.get(channel_idx)
            if channel is None:
                raise FluxUSBError("Recv bad channel idx 0x%02x" % channel_idx)
            if fin == 0xfe:
                channel.on_object(msgpack.unpackb(buf))
            elif fin == 0xff:
                self._send_binary_ack(channel_idx)
                channel.on_binary(buf)
            elif fin == 0x80:
                channel.on_binary_ack()
            else:
                raise FluxUSBError("Recv bad fin 0x%02x" % fin)
        elif channel_idx == 0xf0:
            if fin != 0xfe:
                raise FluxUSBError("Recv bad fin 0x%02x" % fin)
            self._on_channel_ctrl_response(msgpack.unpackb(buf))
        else:
            raise FluxUSBError("Recv bad control channel 0x%02x" % channel_idx)

    def run(self):
        try:
            self.running = True
            while self.running:
                self.run_once()
        except Exception:
            logger.exception("USB run got error")
            self.running = False
            raise

    def stop(self):
        self.running = False

    def send_object(self, channel, obj):
        payload = msgpack.packb(obj)
        buf = HEAD_PACKER.pack(len(payload) + 4, channel) + payload + b"\xfe"
        self._send(buf)

    def send_binary(self, channel, buf):
        buf = HEAD_PACKER.pack(len(buf) + 4, channel) + buf + b"\xff"
        self._send(buf)

    def _on_channel_ctrl_response(self, obj):
        index = obj.get(b"channel")
        status = obj.get(b"status")
        if status == b"ok":
            self.channels[index] = Channel(self, index)
            self.chl_semaphore.release()
        else:
            logger.error("Create channel error: %s", status.decode())

    def _close_channel(self, channel):
        self.send_object(0xf0, {"channel": channel.index, "action": "close"})

    def open_channel(self):
        # Send request
        idx = None
        for i in range(len(self.channels) + 1):
            if self.channels.get(i) is None:
                idx = i
        logger.debug("Request channel %i", idx)
        self.send_object(0xf0, {"channel": idx, "action": "open"})

        self.chl_semaphore.acquire(timeout=3.0)
        channel = self.channels.get(idx)
        if channel:
            return self.channels[idx]
        else:
            raise RuntimeError("Channel creation failed")


class Channel(object):
    def __init__(self, usbprotocol, index):
        self.index = index
        self.usbprotocol = usbprotocol
        self.obj_semaphore = Semaphore(0)
        self.buf_semaphore = Semaphore(0)
        self.ack_semaphore = Semaphore(0)
        self.objq = deque()
        self.bufq = deque()

    def __del__(self):
        self.usbprotocol._close_channel(self)

    def on_object(self, obj):
        self.objq.append(obj)
        self.obj_semaphore.release()

    def on_binary(self, buf):
        self.bufq.append(buf)
        self.buf_semaphore.release()

    def on_binary_ack(self):
        self.ack_semaphore.release()

    def get_object(self, timeout=3.0):
        if self.obj_semaphore.acquire(timeout=timeout) is False:
            raise SystemError("TIMEOUT")
        return self.objq.popleft()

    def get_buffer(self, timeout=3.0):
        if self.buf_semaphore.acquire(timeout=timeout) is False:
            raise SystemError("TIMEOUT")
        return self.bufq.popleft()

    def send_object(self, obj):
        self.usbprotocol.send_object(self.index, obj)

    def send_binary(self, buf, timeout=3.0):
        self.usbprotocol.send_binary(self.index, buf)
        if self.ack_semaphore.acquire(timeout=timeout) is False:
            raise SystemError("TIMEOUT")


class FluxUSBError(Exception):
    pass
