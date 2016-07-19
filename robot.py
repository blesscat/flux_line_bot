import pdb
import time
from fluxclient.encryptor import KeyObject
from fluxclient.robot import FluxRobot
from fluxclient.commands.misc import get_or_create_default_key

def callback(robot_connection, sent, size):
    print('sent: {}'.format(sent))
    print('size: {}'.format(size))
    
client_key = get_or_create_default_key("./sdk_connection.pem")
robot = FluxRobot(("122.116.80.243", 23811), client_key)
print(robot.list_files('/SD'))
pdb.set_trace()
try:
    robot.start()
except:
    pass
#robot.upload_file('test.fc', '/SD/test.fc', process_callback=callback)
print(robot.list_files('/SD'))
