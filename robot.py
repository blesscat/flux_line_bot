import pdb
from fluxclient.encryptor import KeyObject
from fluxclient.robot import FluxRobot
from fluxclient.commands.misc import get_or_create_default_key

client_key = get_or_create_default_key("./sdk_connection.pem")
pdb.set_trace()
robot = FluxRobot(("192.168.30.131", 23811), client_key)
