```{eval-rst}
.. currentmodule:: tango
```

(database)=

# Working with TANGO database

Here we provide some basics, how to interact with TANGO database from Python

## Registering devices

Here is how to define devices in the Tango DataBase:

```
from tango import Database, DbDevInfo

#  A reference on the DataBase
db = Database()

# The 3 devices name we want to create
# Note: these 3 devices will be served by the same DServer
new_device_name1 = "px1/tdl/mouse1"
new_device_name2 = "px1/tdl/mouse2"
new_device_name3 = "px1/tdl/mouse3"

# Define the Tango Class served by this  DServer
new_device_info_mouse = DbDevInfo()
new_device_info_mouse._class = "Mouse"
new_device_info_mouse.server = "ds_Mouse/server_mouse"

# add the first device
print("Creating device: %s" % new_device_name1)
new_device_info_mouse.name = new_device_name1
db.add_device(new_device_info_mouse)

# add the next device
print("Creating device: %s" % new_device_name2)
new_device_info_mouse.name = new_device_name2
db.add_device(new_device_info_mouse)

# add the third device
print("Creating device: %s" % new_device_name3)
new_device_info_mouse.name = new_device_name3
db.add_device(new_device_info_mouse)
```

### Setting up device properties

A more complex example using python subtilities.
The following python script example (containing some functions and instructions
manipulating a Galil motor axis device server) gives an idea of how the Tango
API should be accessed from Python:

```
from tango import DeviceProxy

# connecting to the motor axis device
axis1 = DeviceProxy("microxas/motorisation/galilbox")

# Getting Device Properties
property_names = ["AxisBoxAttachement",
                  "AxisEncoderType",
                  "AxisNumber",
                  "CurrentAcceleration",
                  "CurrentAccuracy",
                  "CurrentBacklash",
                  "CurrentDeceleration",
                  "CurrentDirection",
                  "CurrentMotionAccuracy",
                  "CurrentOvershoot",
                  "CurrentRetry",
                  "CurrentScale",
                  "CurrentSpeed",
                  "CurrentVelocity",
                  "EncoderMotorRatio",
                  "logging_level",
                  "logging_target",
                  "UserEncoderRatio",
                  "UserOffset"]

axis_properties = axis1.get_property(property_names)
for prop in axis_properties.keys():
    print("%s: %s" % (prop, axis_properties[prop][0]))

# Changing Properties
axis_properties["AxisBoxAttachement"] = ["microxas/motorisation/galilbox"]
axis_properties["AxisEncoderType"] = ["1"]
axis_properties["AxisNumber"] = ["6"]
axis1.put_property(axis_properties)
```
