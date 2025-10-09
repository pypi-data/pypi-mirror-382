```{eval-rst}
.. currentmodule:: tango
```

(pytango-data-types)=

# Data types

This chapter describes the mapping of data types between Python and Tango.

Tango has more data types than Python which is more dynamic. The input and
output values of the commands are translated according to the array below.
Note that the numpy type is used for the input arguments.
Also, it is recommended to use numpy arrays of the appropiate type for output
arguments as well, as they tend to be much more efficient.

**For scalar types (SCALAR)**

```{eval-rst}
+-------------------------+---------------------------------------------------------------------------+
|   Tango data type       |              Python data type                                             |
+=========================+===========================================================================+
| DEV_VOID                |                    No data                                                |
+-------------------------+---------------------------------------------------------------------------+
| DEV_BOOLEAN             | :py:obj:`bool`                                                            |
+-------------------------+---------------------------------------------------------------------------+
| DEV_SHORT               | :py:obj:`int`                                                             |
+-------------------------+---------------------------------------------------------------------------+
| DEV_LONG                | :py:obj:`int`                                                             |
+-------------------------+---------------------------------------------------------------------------+
| DEV_LONG64              | :py:obj:`int`                                                             |
+-------------------------+---------------------------------------------------------------------------+
| DEV_FLOAT               | :py:obj:`float`                                                           |
+-------------------------+---------------------------------------------------------------------------+
| DEV_DOUBLE              | :py:obj:`float`                                                           |
+-------------------------+---------------------------------------------------------------------------+
| DEV_USHORT              | :py:obj:`int`                                                             |
+-------------------------+---------------------------------------------------------------------------+
| DEV_ULONG               | :py:obj:`int`                                                             |
+-------------------------+---------------------------------------------------------------------------+
| DEV_ULONG64             | :py:obj:`int`                                                             |
+-------------------------+---------------------------------------------------------------------------+
| DEV_STRING              | :py:obj:`str` (decoded with *latin-1*, aka *ISO-8859-1*)                  |
+-------------------------+---------------------------------------------------------------------------+
|                         | sequence of two elements:                                                 |
| DEV_ENCODED             |                                                                           |
|                         | 0. :py:obj:`str` (decoded with *latin-1*, aka *ISO-8859-1*)               |
| (*New in PyTango 8.0*)  | 1. :py:obj:`bytes` (for any value of *extract_as*, except String.         |
|                         |    In this case it is :py:obj:`str` (decoded with default python          |
|                         |    encoding *utf-8*))                                                     |
+-------------------------+---------------------------------------------------------------------------+
|                         | * :py:obj:`int` (for value)                                               |
|                         | * :py:class:`list` <:py:obj:`str`>  (for enum_labels)                     |
| DEV_ENUM                |                                                                           |
|                         | Note:                                                                     |
| (*New in PyTango 9.0*)  | Direct attribute access via DeviceProxy will return                       |
|                         | :py:obj:`enum.IntEnum`.                                                   |
+-------------------------+---------------------------------------------------------------------------+
```

**For array types (SPECTRUM/IMAGE)**

```{eval-rst}
+-------------------------+-----------------+-------------------------------------------------------------------------+
|    Tango data type      |   ExtractAs     |             Python data type                                            |
+=========================+=================+=========================================================================+
| DEVVAR_CHARARRAY        | Numpy           | :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.uint8`)                |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Bytes           | :py:obj:`bytes`                                                         |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | ByteArray       | :py:obj:`bytearray`                                                     |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | String          | :py:obj:`str`                                                           |
|                         |                 |                                                                         |
|                         |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | List            | :py:class:`list` <:py:obj:`int`>                                        |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Tuple           | :py:class:`tuple` <:py:obj:`int`>                                       |
+-------------------------+-----------------+-------------------------------------------------------------------------+
| DEVVAR_SHORTARRAY       | Numpy           | :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.uint16`)               |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_SHORT + SPECTRUM)  | Bytes           | :py:obj:`bytes`                                                         |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_SHORT + IMAGE)     | ByteArray       | :py:obj:`bytearray`                                                     |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | String          | :py:obj:`str`                                                           |
|                         |                 |                                                                         |
|                         |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | List            | :py:class:`list` <:py:obj:`int`>                                        |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Tuple           | :py:class:`tuple` <:py:obj:`int`>                                       |
+-------------------------+-----------------+-------------------------------------------------------------------------+
| DEVVAR_LONGARRAY        | Numpy           | :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.uint32`)               |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_LONG + SPECTRUM)   | Bytes           | :py:obj:`bytes`                                                         |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_LONG + IMAGE)      | ByteArray       | :py:obj:`bytearray`                                                     |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | String          | :py:obj:`str`                                                           |
|                         |                 |                                                                         |
|                         |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | List            | :py:class:`list` <:py:obj:`int`>                                        |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Tuple           | :py:class:`tuple` <:py:obj:`int`>                                       |
+-------------------------+-----------------+-------------------------------------------------------------------------+
| DEVVAR_LONG64ARRAY      | Numpy           | :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.uint64`)               |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_LONG64 + SPECTRUM) | Bytes           | :py:obj:`bytes`                                                         |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_LONG64 + IMAGE)    | ByteArray       | :py:obj:`bytearray`                                                     |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | String          | :py:obj:`str`                                                           |
|                         |                 |                                                                         |
|                         |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | List            | :py:class:`list` <:py:obj:`int`>                                        |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Tuple           | :py:class:`tuple` <:py:obj:`int`>                                       |
+-------------------------+-----------------+-------------------------------------------------------------------------+
| DEVVAR_FLOATARRAY       | Numpy           | :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.float32`)              |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_FLOAT + SPECTRUM)  | Bytes           | :py:obj:`bytes`                                                         |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_FLOAT + IMAGE)     | ByteArray       | :py:obj:`bytearray`                                                     |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | String          | :py:obj:`str`                                                           |
|                         |                 |                                                                         |
|                         |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | List            | :py:class:`list` <:py:obj:`float`>                                      |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Tuple           | :py:class:`tuple` <:py:obj:`float`>                                     |
+-------------------------+-----------------+-------------------------------------------------------------------------+
| DEVVAR_DOUBLEARRAY      | Numpy           | :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.float64`)              |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_DOUBLE + SPECTRUM) | Bytes           | :py:obj:`bytes`                                                         |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_DOUBLE + IMAGE)    | ByteArray       | :py:obj:`bytearray`                                                     |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | String          | :py:obj:`str`                                                           |
|                         |                 |                                                                         |
|                         |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | List            | :py:class:`list` <:py:obj:`float`>                                      |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Tuple           | :py:class:`tuple` <:py:obj:`float`>                                     |
+-------------------------+-----------------+-------------------------------------------------------------------------+
| DEVVAR_USHORTARRAY      | Numpy           | :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.uint16`)               |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_USHORT + SPECTRUM) | Bytes           | :py:obj:`bytes`                                                         |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_USHORT + IMAGE)    | ByteArray       | :py:obj:`bytearray`                                                     |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | String          | :py:obj:`str`                                                           |
|                         |                 |                                                                         |
|                         |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | List            | :py:class:`list` <:py:obj:`int`>                                        |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Tuple           | :py:class:`tuple` <:py:obj:`int`>                                       |
+-------------------------+-----------------+-------------------------------------------------------------------------+
| DEVVAR_ULONGARRAY       | Numpy           | :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.uint32`)               |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_ULONG + SPECTRUM)  | Bytes           | :py:obj:`bytes`                                                         |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_ULONG + IMAGE)     | ByteArray       | :py:obj:`bytearray`                                                     |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | String          | :py:obj:`str`                                                           |
|                         |                 |                                                                         |
|                         |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | List            | :py:class:`list` <:py:obj:`int`>                                        |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Tuple           | :py:class:`tuple` <:py:obj:`int`>                                       |
+-------------------------+-----------------+-------------------------------------------------------------------------+
| DEVVAR_ULONG64ARRAY     | Numpy           | :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.uint64`)               |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_ULONG64 + SPECTRUM)| Bytes           | :py:obj:`bytes`                                                         |
|                         +-----------------+-------------------------------------------------------------------------+
| (DEV_ULONG64 + IMAGE)   | ByteArray       | :py:obj:`bytearray`                                                     |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | String          | :py:obj:`str`                                                           |
|                         |                 |                                                                         |
|                         |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | List            | :py:class:`list` <:py:obj:`int`>                                        |
|                         +-----------------+-------------------------------------------------------------------------+
|                         | Tuple           | :py:class:`tuple` <:py:obj:`int`>                                       |
+-------------------------+-----------------+-------------------------------------------------------------------------+
| DEVVAR_STRINGARRAY      |                 | sequence<:py:obj:`str`>                                                 |
|                         |                 |                                                                         |
| (DEV_STRING + SPECTRUM) |                 | (decoded with *latin-1*, aka *ISO-8859-1*)                              |
|                         |                 |                                                                         |
| (DEV_STRING + IMAGE)    |                 |                                                                         |
+-------------------------+-----------------+-------------------------------------------------------------------------+
|                         |                 | sequence of two elements:                                               |
|  DEV_LONGSTRINGARRAY    |                 |                                                                         |
|                         |                 | 0. :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.int32`) or          |
|                         |                 |    sequence<:py:obj:`int`>                                              |
|                         |                 | 1.  sequence<:py:obj:`str`> (decoded with *latin-1*, aka *ISO-8859-1*)  |
+-------------------------+-----------------+-------------------------------------------------------------------------+
|                         |                 | sequence of two elements:                                               |
|  DEV_DOUBLESTRINGARRAY  |                 |                                                                         |
|                         |                 | 0. :py:class:`numpy.ndarray` (dtype= :py:obj:`numpy.float64`) or        |
|                         |                 |    sequence<:py:obj:`int`>                                              |
|                         |                 | 1. sequence<:py:obj:`str`> (decoded with *latin-1*, aka *ISO-8859-1*)   |
+-------------------------+-----------------+-------------------------------------------------------------------------+
```

For SPECTRUM and IMAGES the actual sequence object used depends on the context
where the tango data is used.

1. for properties the sequence is always a {py:class}`list`. Example:

   ```pycon
   >>> import tango
   >>> db = tango.Database()
   >>> s = db.get_property(["TangoSynchrotrons"])
   >>> print type(s)
   <type 'list'>
   ```

2. for attribute/command values:

   - For non-string data types: {py:class}`numpy.ndarray`
   - For string data types:
     - {py:class}`tuple` \<{py:class}`str`> for clients reading attributes
     - {py:class}`list` \<{py:class}`str`> in attribute write and command handlers within devices

(pytango-devenum-data-types)=

## DevEnum pythonic usage

When using regular tango DeviceProxy and AttributeProxy DevEnum is treated just
like in cpp tango (see [enumerated attributes](https://tango-controls.readthedocs.io/en/latest/How-To/development/cpp/how-to-enumerated-attribute.html#how-to-enumerated-attribute)
for more info). However, since PyTango >= 9.2.5 there is a more pythonic way of
using DevEnum data types if you use the {ref}`high level API <pytango-hlapi>`,
both in server and client side.

:::{note}
DevEnum is only support for device attributes, not for commands.
:::

In server side you can use python {py:obj}`enum.IntEnum` class to deal with
DevEnum attributes (here we use type hints, see {ref}`type-hint`, but we can also set
`dtype=Noon` when defining the attribute - see earlier versions of this documentation):

```{code-block} python
import time
from enum import IntEnum

from tango.server import Device, attribute, command


class Noon(IntEnum):
    AM = 0  # DevEnum's must start at 0
    PM = 1  # and increment by 1


class DisplayType(IntEnum):
    ANALOG = 0  # DevEnum's must start at 0
    DIGITAL = 1  # and increment by 1


class Clock(Device):
    display_type = DisplayType.ANALOG

    @attribute
    def time(self) -> float:
        return time.time()

    @attribute(max_dim_x=9)
    def gmtime(self) -> tuple[int]:
        return time.gmtime()

    @attribute
    def noon(self) -> Noon:
        time_struct = time.gmtime(time.time())
        return Noon.AM if time_struct.tm_hour < 12 else Noon.PM

    @attribute
    def display(self) -> DisplayType:
        return self.display_type

    @display.setter
    def display(self, display_type: int):
        # note that we receive an integer, not an enum instance,
        # so we have to convert that to an instance of our enum.
        self.display_type = DisplayType(display_type)

    @command(dtype_in=float, dtype_out=str)
    def ctime(self, seconds):
        """
        Convert a time in seconds since the Epoch to a string in local time.
        This is equivalent to asctime(localtime(seconds)). When the time tuple
        is not present, current time as returned by localtime() is used.
        """
        return time.ctime(seconds)

    @command
    def mktime(self, tupl: tuple[int]) -> float:
        return time.mktime(tuple(tupl))


if __name__ == "__main__":
    Clock.run_server()
```

On the client side you can also use a pythonic approach for using DevEnum attributes:

```{code-block} python
import sys
import tango

if len(sys.argv) != 2:
    print("must provide one and only one clock device name")
    sys.exit(1)

clock = tango.DeviceProxy(sys.argv[1])
t = clock.time
gmt = clock.gmtime
noon = clock.noon
display = clock.display
print(t)
print(gmt)
print(noon, noon.name, noon.value)
if noon == noon.AM:
    print("Good morning!")
print(clock.ctime(t))
print(clock.mktime(gmt))
print(display, display.name, display.value)
clock.display = display.ANALOG
clock.display = "DIGITAL"  # you can use a valid string to set the value
print(clock.display, clock.display.name, clock.display.value)
display_type = type(display)  # or even create your own IntEnum type
analog = display_type(0)
clock.display = analog
print(clock.display, clock.display.name, clock.display.value)
clock.display = clock.display.DIGITAL
print(clock.display, clock.display.name, clock.display.value)
```

Example output:

```console
$ python client.py test/clock/1
1699433430.714272
[2023   11    8    8   50   30    2  312    0]
0 AM 0
Good morning!
Wed Nov  8 09:50:30 2023
1699429830.0
0 ANALOG 0
1 DIGITAL 1
0 ANALOG 0
1 DIGITAL 1
```
