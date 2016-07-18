from flux import FLUX
from fluxclient.upnp import UpnpError
from fluxclient.commands.misc import get_or_create_default_key
from fluxclient.encryptor import KeyObject

def add_rsa():
    my_rsakey = get_or_create_default_key("./sdk_connection.pem")
    flux = FLUX(("122.116.80.243", 1901))
    flux.poke()

    upnp_task = flux.device.manage_device(my_rsakey)
    try:
        upnp_task.authorize_with_password("dxi013") #It's the same password you entered in FLUX Studio's configuration page.
        upnp_task.add_trust("my_public_key", my_rsakey.public_key_pem.decode())
        print("Authorized")
        return "Authorized"
    except UpnpError as e:
        print("Authorization failed: %s" % e)
        return "Fail"
