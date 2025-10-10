# facade_sdk

# # About SDK
This package is for the Smart Manufactory Research on the FANUC robot. This is mainy for the publisher devices who need to send data to the defined broker. Rather than having devices create their own MQTT connection, this facade hides those details and makes it easy for devices to send data by simply creating a client object. 

# # Installing Library
To install, run `pip install facade-sdk`. You can also download the code via this github.

# # How to Use
After installing the library, you can start creating a user object to send data. See test for the full code.

1. Import the libary: `from package.client import Client`
2. Create client object: `client = Client(broker_ip="", client_type=Client.CAMERA, device_id="Camera923", auto_connect=True, broker_port=1234, timeout=60)`

- broker_ip is the IP address of the broker. Please ask DATA TEAM for what that address is. It needs to be as a string.

- client_type is the type of client you are. There are currently four options: CAMERA, IMU, AI, and ROBOT. They are static so you can either type them as a string or use `Client.<type>` where the <type> is one of the options.

- device_id is the ID of the device. This can be anything as a string, but would be more helpful if it is the physical ID of that device.

- auto_connect is set to True by default. Once you create the object, it will autoconnect to the broker but it is possible to connect manually.

- broker_port is set by default to 1883 but can change if needed or if there is multiple brokers.

- timeout is how long till a connection timeout occurs or broker doesn't respond in time. Defaultly set as 60.

3. Publish data: `client.publish("Hi there!")`

- You can publish anything but needs to be a string. Processing will take the string into a json so it is perferly if it in json format or csv format.

# # PyPI Ownership
Currently, Michael Seavers has access to the PyPI library. If you continue to use the package and need to update it, you either need to transfer ownership by emailing (MichaelSeavers@hotmail.com) or create your own PyPI account and remake the package. 

# # PyPI Building
`python -m build` to rebuild dependencies and then `twin upload dist/*` when ready to push. You will need the API ID. Contact Michael for the information.