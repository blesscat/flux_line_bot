import pdb
import socket
import struct

from uuid import UUID
from io import BytesIO

from fluxclient.encryptor import KeyObject
from fluxclient.upnp.device import Device
from fluxclient.upnp.misc import validate_identify


class FLUX(object):
    def __init__(self, device_ipaddr):
        self.device_ipaddr = device_ipaddr
        self.payload = struct.pack("<4sBB16s", b"FLUX", 1, 0, UUID(int=0).bytes)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))
        self.serial = ''
        self.uuid = ''
        self.status = {}

    def poke(self):
        self.sock.sendto(self.payload, self.device_ipaddr)
        buf, endpoint = self.sock.recvfrom(4096)
        if len(buf) < 8:
            return False
        try:
            magic_num, proto_ver, action_id = struct.unpack("4sBB", buf[:6])
            if magic_num != b"FLUX":
            # Bad magic number
                return
            self.handle_message(endpoint, buf[6:])

        except struct.error:
            print("Payload error: %s", repr(buf))

    def handle_message(self, endpoint, payload):
        args = struct.unpack("<16s10sfHH", payload[:34])
        uuid_bytes, bsn, master_ts = args[:3]
        l_master_pkey, l_signuture = args[3:]
        self.serial = sn = bsn.decode("ascii")
        self.uuid = uuid = UUID(bytes=uuid_bytes)

        f = BytesIO(payload[34:])
        masterkey_doc = f.read(l_master_pkey)
        signuture = f.read(l_signuture)

        if not validate_identify(uuid, signuture, serial=sn,
                                 masterkey_doc=masterkey_doc):
           print("Validate identify failed (uuid=%s)", uuid)
           return

        master_pkey = KeyObject.load_keyobj(masterkey_doc)

        stbuf = f.read(64)
        st_ts, st_id, st_prog, st_head, st_err = \
            struct.unpack("dif16s32s", stbuf)

        head_module = st_head.decode("ascii",
                                     "ignore").strip("\x00")
        error_label = st_err.decode("ascii",
                                    "ignore").strip("\x00")

        self.device = Device(uuid, sn, master_pkey, 1)
        self.device.update_status(st_id=st_id, st_ts=st_ts, st_prog=st_prog,
                             head_module=head_module,
                             error_label=error_label)
        self.status = self.device.status

if __name__ == "__main__":
    flux = FLUX(("122.116.80.243", 1901))
    flux.poke()
    print(vars(flux))
    print(vars(flux.device))
    print(flux.status)
    

