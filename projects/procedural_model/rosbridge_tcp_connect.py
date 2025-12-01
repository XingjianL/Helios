import socket
import bson
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("172.20.218.12", 9090))

# Advertise topic
advertise_msg = {
    "op": "advertise",
    "topic": "/my_string",
    "type": "std_msgs/String"
}
s.sendall(bson.BSON.encode(advertise_msg))
time.sleep(0.1)

# Publish messages
for i in range(10):
    publish_msg = {
        "op": "publish",
        "topic": "/my_string",
        "msg": {"data": f"hello {i} over tcp"}
    }
    s.sendall(bson.BSON.encode(publish_msg))
    time.sleep(1)

s.close()
