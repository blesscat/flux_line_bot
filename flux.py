import os

import socket
import struct
import pdb
from time import time, sleep

from uuid import UUID
from io import BytesIO

from fluxclient.encryptor import KeyObject
from fluxclient.upnp.device import Device
from fluxclient.upnp.misc import validate_identify
from fluxclient.utils.version import StrictVersion
from fluxclient.upnp import UpnpError
from fluxclient.commands.misc import get_or_create_default_key


class FLUX(object):
    def __init__(self, device_ipaddr):
        self.device_ipaddr = device_ipaddr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)
        self.sock.bind(('', 0))
        self.serial = ''
        self.uuid = ''
        self.status = {}
        self.poke()

    def poke(self):
        self.payload = struct.pack("<4sBB16s", b"FLUX", 1, 0, UUID(int=0).bytes)
        self.sock.sendto(self.payload, self.device_ipaddr)
        try:
            buf, endpoint = self.sock.recvfrom(4096)
            if len(buf) < 8:
                return False
            magic_num, proto_ver, action_id = struct.unpack("4sBB", buf[:6])
            if magic_num != b"FLUX":
            # Bad magic number
                return
            
            self.handle_message(endpoint, buf[6:])


            self.payload = struct.pack("<4sBB16s", b"FLUX", 1, 2, self.uuid.bytes)
            self.sock.sendto(self.payload, self.device_ipaddr)
            magic_num, proto_ver, action_id = struct.unpack("4sBB", buf[:6])
            buf, endpoint = self.sock.recvfrom(4096)
            self.handle_touch(endpoint, buf[6:])

            self.status = self.device.status

        except socket.timeout:
            return False
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

    def handle_touch(self, endpoint, payload):
        f = BytesIO(payload)

        buuid, master_ts, l1, l2 = struct.unpack("<16sfHH", f.read(24))
        uuid = UUID(bytes=buuid)

        #if not self.server.source_filter(uuid, endpoint):
        #    # Ingore this uuid
        #    return

        slavekey_str = f.read(l1)
        slavekey_signuture = f.read(l2)
        temp_pkey = KeyObject.load_keyobj(slavekey_str)

        bmeta = f.read(struct.unpack("<H", f.read(2))[0])
        smeta = bmeta.decode("utf8")
        rawdata = {}
        for item in smeta.split("\x00"):
            if "=" in item:
                k, v = item.split("=", 1)
                rawdata[k] = v

        doc_signuture = f.read()
        master_key = self.device.master_key

        if master_key.verify(payload[16:20] + slavekey_str,
                             slavekey_signuture):
            if temp_pkey.verify(bmeta, doc_signuture):
                self.device.slave_timestemp = master_ts
                self.device.slave_key = temp_pkey
                self.device.has_password = rawdata.get("pwd") == "T"
                self.device.timestemp = float(rawdata.get("time", 0))
                self.device.timedelta = self.device.timestemp - time()

                self.device.model_id = rawdata.get("model", "UNKNOW_MODEL")
                self.device.version = StrictVersion(rawdata["ver"])
                self.device.name = rawdata.get("name", "NONAME")

                self.device.discover_endpoint = endpoint
                self.device.ipaddr = endpoint[0]

                return uuid
            else:
                print("Slave key signuture error (V1)")
        else:
            print("Master key signuture error (V1)")
    
    def add_rsa(self):
        my_rsakey = get_or_create_default_key("./sdk_connection.pem")
        upnp_task = self.device.manage_device(my_rsakey)
        try:
            upnp_task.authorize_with_password(os.environ['password']) #It's the same password you entered in FLUX Studio's configuration page.
            upnp_task.add_trust("my_public_key", my_rsakey.public_key_pem.decode())
            print("Authorized")
            return "Authorized"
        except UpnpError as e:
            error_code = "Authorization failed: %s" % e
            return error_code
        
if __name__ == "__main__":
    while True:
        Flux = FLUX(("0.0.0.0", 1901))
        print(Flux.status)
        sleep(1)


