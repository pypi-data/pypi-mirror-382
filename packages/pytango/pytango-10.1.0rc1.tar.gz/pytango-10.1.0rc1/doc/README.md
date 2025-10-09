# PyTango Documentation

PyTango's documentation is written in [MyST](https://myst-parser.readthedocs.io/), a rich and extensible
flavour of Markdown, and built with [Sphinx](http://www.sphinx-doc.org/en/stable).

To build the docs locally, you will need to [install pixi](https://pixi.sh/latest/#installation), and then run:

```console
$ cd /path/to/pytango
$ pixi run doc
```

There is also a `pixi run doc_no_cache` option to rebuild the docs completely.  This is useful when
the only change is in a docstring, and Sphinx is not picking it up.

After building, open the `build/sphinx/index.html` page in your browser.

Another alternative is `pixi run doc_live`, which will automatically rebuild
Sphinx documentation on changes, with hot reloading in the browser
using [sphinx-autobuild](https://github.com/sphinx-doc/sphinx-autobuild#readme).
