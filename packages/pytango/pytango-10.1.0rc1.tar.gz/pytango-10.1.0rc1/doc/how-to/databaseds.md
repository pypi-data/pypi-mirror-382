```{eval-rst}
.. currentmodule:: tango
```

```{highlight} python
:linenothreshold: 4
```

(databaseds)=

# PyTango Database Device Server

The Tango Database device (usually `sys/database/2`) is what all other
devices use to get their configuration and to coordinate with each
other. It must be running in order for a Tango control system to work.

The standard Database device server is implemented in C++ and requires
a running MySQL or MariaDB server to operate, which means it can be
challenging to set up.

PyTango contains its own Database implementation, which conforms to the
C++ one and should work as a drop-in replacement. It stores data using
`sqlite3` so it has no external dependencies. It can be useful for a
local development environment, CI testing and, eventually, perhaps
even a small control system setup.

:::{warning}
This implementation is in an experimental state, and has not
been extensively tested for compatibility or for performance.
Don't use it for anything mission critical!
:::

To run it:

```console
$ TANGO_HOST=localhost:11000 python -m tango.databaseds.database 2
```

Now you should be able to start Tango devices and use tools like Jive,
just make sure to set `TANGO_HOST=localhost:11000`.

The sqlite3 database is stored in your current working directory, as
`tango_database.db`. To start over from scratch, just remove this file.

The port number can be selected freely, but 10000 is the standard
Tango port, so choose another one if you need to run in parallel with
an existing control system.
