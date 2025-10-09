# Welcome to PyTango documentation!

PyTango is a python module that exposes to [Python](https://www.python.org) the complete [Tango C++ API](https://tango-controls.github.io/cppTango-docs/index.html).
This means that you can write not only [Tango](https://www.tango-controls.org/) applications (scripts, CLIs, GUIs)
that access Tango device servers but also Tango device servers themselves, all of this in pure python.

PyTango also includes a Pythonic high-level API that makes using it *much* easier than the Tango C++ API!

```{image} _static/banner.png
:scale: 40%
:align: center
```

Check out the [installation guide](#installation-guide) to learn how to build and/or install PyTango and after that the
[tutorials](#tutorial-guide) can help you with the first steps in the PyTango world.
If you need help understanding what Tango itself really is, you can check the
[Tango docs](inv:tangodoc:std#index) where you will find plenty of explanations and tutorials.

```{toctree}
:maxdepth: 2
:titlesonly: true
:hidden: true

installation
tutorial
how-to
API reference <api>
News and releases <versions_news>
TEP <tep>
Index <genindex>
```
