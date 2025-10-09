# SPDX-FileCopyrightText: All Contributors to the PyTango project
# SPDX-License-Identifier: LGPL-3.0-or-later
def test_import_aliased_module():

    import PyTango

    assert PyTango is not None
