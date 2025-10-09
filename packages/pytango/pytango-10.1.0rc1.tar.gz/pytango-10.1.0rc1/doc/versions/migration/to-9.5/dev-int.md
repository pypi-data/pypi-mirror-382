(to9.5-dev-int)=

# Removal of DevInt

In PyTango v9.5.0 the {class}`~tango.CmdArgType.DevInt` data type was removed from PyTango because the corresponding
`DEV_INT` type was [removed from cppTango](https://gitlab.com/tango-controls/cppTango/-/issues/1108).
The {class}`~tango.CmdArgType.DevInt` didn't function correctly, but the nearest
replacement is {class}`~tango.CmdArgType.DevLong`.
