```{eval-rst}
.. currentmodule:: tango
```

```{highlight} python
:linenothreshold: 3
```

(how-to-contribute)=

# How to Contribute

Everyone is welcome to contribute to the PyTango project.
If you don't feel comfortable writing core PyTango, we are looking for contributors to documentation or/and tests.

## Report a bug

Bugs can be reported as issues in [PyTango repository](https://gitlab.com/tango-controls/pytango/issues).

It is helpful if you include the PyTango version information in your issue's description.
It can be a dump of:

```console
$ python -c "import tango; print(tango.utils.info())"
```

## Workflow

A Git feature branch workflow is used. More details can be seen in this [tutorial].
Good practices:

- For commit messages the first line should be short (50 chars or less) and contain a summary
  of all changes. Provide more detail in additional paragraphs unless the change is trivial.
- Merge requests (MRs) should be ALWAYS made to the `develop` branch.

## MyST and Sphinx

Documentation is written in [MyST], a rich and extensible flavour of Markdown, and built with [Sphinx] - it's easy to contribute.
It also uses [autodoc] importing docstrings from tango package.

:::{note}
Docstrings still need to be written in [reStructuredText]
:::

To test the docs locally with [pixi] (see [Using pixi for developement](#pixi-for-development)):

```console
$ cd /path/to/pytango
$ pixi run doc
```

There is also a `pixi run doc_no_cache` option to rebuild the docs completely.  This is useful when
the only change is in a docstring, and Sphinx is not picking it up.

After building, open the `build/sphinx/index.html` page in your browser.

When working on the documentation, you can run `pixi run doc_live` to rebuild Sphinx documentation on changes, with hot reloading in the browser using [sphinx-autobuild](https://github.com/sphinx-doc/sphinx-autobuild#readme).

## Source code standard

All code should be [PEP8] compatible. We have set up checking code quality with
[pre-commit] which runs [ruff], a Python linter written in Rust. `pre-commit` is
run as first job in every gitlab-ci pipeline and will fail if errors are detected.

It is recommended to install [pre-commit] locally to check code quality on every commit,
before to push to GitLab. This is a one time operation:

- Install [pre-commit]. [pipx] is a good way if you use it.
  Otherwise, see the [official documentation](https://pre-commit.com/#install).
- Run `pre-commit install` at the root of your `pytango` repository.

That's it. `pre-commit` will now run automatically on every commit.
If errors are reported, the commit will be aborted.
You should fix them and try to commit again.

Note that you can also configure your editor to run `ruff`.
See [ruff README](https://github.com/charliermarsh/ruff#editor-integrations).

(pixi-for-development)=

## Using pixi for development

If you like to be at the forefront and aren't afraid of trying new tools, you should give [pixi] a try.
Pixi is a package manager and workflow tool built on the foundation of the conda ecosystem.
It provides developers with an easy interface to manage environments and run tasks.
The same commands work on all platforms (Linux, macOS and Windows).

`pixi` comes as a single executable.
Refer to [pixi installation](https://pixi.sh/latest/#installation) for more information.

:::{warning}
Pixi is still in activate development. Ensure you have the latest version available.
:::

To compile and install pytango in editable mode, run:
: - `$ pixi run install`

This will automatically create a conda environment with all required dependencies.

To check that pytango was installed properly, you can use `pixi run check`, which is just a shortcut for
`pixi run python -c 'import tango; print(tango.utils.info())'`. That will print information about the
pytango version installed in the environment.

To run all the tests:
: - `$ pixi run test`

You can run part of the tests by passing any argument to `pytest`:
: - `$ pixi run pytest -k test_ping`

All previous commands will run in the `default` environment (with latest python version).
To test with a different python version, you can pass another environment to the `pixi run` command.

To install and test pytango in the `py311` env:
: - `$ pixi run -e py311 install`
  - `$ pixi run -e py311 pytest`

Run `pixi info` to get a list of all defined environments.

(conda-for-development)=

## Using Conda for development

If you don't want to use `pixi`, you can of course create and work in your own [Conda environment](#build-from-source).

To run the tests locally (after activating your Conda environment):
: - `$ pytest`

To run only some tests, use a filter argument, `-k`:
: - `$ pytest -k test_ping`

## Using Docker for development

Developing using a native pixi/conda environment is faster.  However, it is also possible to use
Docker containers for developing, testing and debugging PyTango.
Use the same manylinux-based image we use for building the Linux binary wheels in CI, for example:
\- `docker run --rm -ti registry.gitlab.com/tango-controls/docker/pytango-builder:manylinux2014_x86_64_v2.0.0`

For direct usage, rather than PyTango development, Docker images with PyTango already
installed are available from the
[Square Kilometre Array Organisation's repository](https://harbor.skao.int/account/sign-in?globalSearch=ska-tango-images-tango-pytango).

For example:
: - `docker run --rm -ti harbor.skao.int/production/ska-tango-images-tango-pytango:9.5.0`

## Releasing a new version

Starting from 9.4.2 pytango tries to follow cpptango releases with the delay up to ~1 month.
The basic steps to make a new release are as follows:

Pick a version number
: - A 3-part version numbering scheme is used:  \<major>.\<minor>.\<patch>
  - Note that PyTango **does not** follow [Semantic Versioning](https://semver.org).
    API changes can occur at minor releases (but avoid them if at all possible).
  - The major and minor version fields (e.g., 9.4) track the TANGO C++ core version.
  - Small changes are done as patch releases.  For these the version
    number should correspond the current development number since each
    release process finishes with a version bump.
  - Patch release example:
    : - `9.4.4.devN` or `9.4.4rcN` (current development branch)
      - changes to `9.4.4` (the actual release)
      - changes to `9.4.5.dev0` (bump the patch version at the end of the release process)
  - Minor release example:
    : - `9.4.4.devN` or `9.4.4rcN` (current development branch)
      - changes to `9.5.0` (the actual release)
      - changes to `9.5.1.dev0` (bump the patch version at the end of the release process)

Check which versions of Python should this release support
: - Follow the [version policy](#pytango-version-policy) and modify correspondingly `requires-python`, `classifiers`,
    and minimum runtime `dependencies` for NumPy in `pyproject.toml`.
    And the `find_package (Python` line in `CMakeLists.txt`.

Create an issue in GitLab
: - This is to inform the community that a release is planned.

  - Use a checklist similar to the one below:

    Task list:

    - \[ \] Read steps in the how-to-contribute docs for making a release

    - \[ \] Release candidate testing and fixes complete

    - \[ \] Merge request to update changelog and bump version

    - \[ \] Merge MR (this is the last MR for the release)

    - \[ \] Make sure CI is OK on develop branch

    - \[ \] Make sure the documentation is updated for develop (readthedocs)

    - \[ \] Create an annotated tag from develop branch

    - \[ \] Push stable to head of develop

    - \[ \] Make sure the documentation is updated for release (readthedocs)

    - \[ \] Check the new version was automatically uploaded to PyPI

    - \[ \] Bump the version with "-dev" in the develop branch

    - \[ \] Create and fill in the release description on GitLab

    - \[ \] Build conda packages

    - \[ \] Advertise the release on the mailing list

    - \[ \] Close this issue

  - A check list in this form on GitLab can be ticked off as the work progresses.

Make a branch from `develop` to prepare the release
: - Example branch name: `prepare-v9.4.4`.
  - Edit the changelog (in `docs/revision.rst`).  Include *all* merge requests
    since the version was bumped after the previous release.  Reverted merge
    requests can be omitted.  A command like this could be used to see all the MR numbers, just change the
    initial version:
    `git log --ancestry-path v9.4.3..develop | grep "merge request" | sort`
  - Find the versions of the dependencies included in our binary PyPI packages, and update this in `docs/news.md`.
    : - For Linux, see [PyTango CI wheel-linux config](https://gitlab.com/tango-controls/pytango/-/blob/c0812e6b50aca9225939ad6d95bf9546736fac4d/.gitlab-ci.yml#L35),
        and [pytango-builder tags](https://gitlab.com/tango-controls/docker/pytango-builder/-/tags),
      - For Windows:  See [cppTango CI config](https://gitlab.com/tango-controls/cppTango/-/blob/9.5.0/.windows-gitlab-ci.yml?ref_type=tags#L17-21),
        [zmq-windows-ci CI config](https://github.com/tango-controls/zmq-windows-ci/blob/master/appveyor.yml),
        and [PyTango CI wheel-win config](https://gitlab.com/tango-controls/pytango/-/blob/c0812e6b50aca9225939ad6d95bf9546736fac4d/.gitlab-ci.yml#L72).
      - For macOS:  see PyTango CI output, and [cpptango conda-forge feedstock](https://github.com/conda-forge/cpptango-feedstock/)
        CI output (for tango-idl).
  - Bump the versions (`tango/release.py`, `pyproject.toml` and `CMakeLists.txt`).
    E.g. `version_info = (9, 4, 4)`, `version = "9.4.4"`, and `VERSION 9.4.4` for a final release.  Or, for
    a release candidate: `version_info = (9, 4, 4, "rc", 1)`, `version = "9.4.4.rc1"`, and `VERSION 9.4.4`.
  - Create a merge request to get these changes reviewed and merged before proceeding.

Make sure CI is OK on `develop` branch
: - On Gitlab CI all tests, on all versions of Python, must be passing.
    If not, bad luck - you'll have to fix it first, and go back a few steps...

Make sure the documentation is updated
: - Log in to <https://readthedocs.org>.
  - Get account permissions for <https://readthedocs.org/projects/pytango> from another
    contributor, if necessary.
  - Readthedocs *should* automatically build the docs for each:
    : - push to develop (latest docs)
      - new tags (e.g v9.4.4)
  - *But*, the webhooks are somehow broken, so it probably won't work automatically!
    : - Trigger the builds manually here:  <https://readthedocs.org/projects/pytango/builds/>
      - Set the new version to "active" here:
        <https://readthedocs.org/dashboard/pytango/versions/>

Create an annotated tag for the release
: - GitLab's can be used to create the tag, but a message must be included.
    We don't want lightweight tags.
  - Alternatively, create tag from the command line (e.g., for version 9.4.4):
    : - `$ git checkout develop`
      - `$ git pull`
      - `$ git tag -a -m "tag v9.4.4" v9.4.4`
      - `$ git push -v origin refs/tags/v9.4.4`

Push `stable` to head of `develop`
: - **Skip this step for release candidates!**

  - Merge `stable` into the latest `develop`.  It is recommended to do a
    fast-forward merge in order to avoid a confusing merge commit. This can be
    done by simply pushing `develop` to `stable` using this command:

    > `$ git push origin develop:stable`

    This way the release tag corresponds to the actual release commit both on the
    `stable` and `develop` branches.

  - In general, the `stable` branch should point to the latest release.

Upload the new version to PyPI
: - The source tarball and binary wheels are automatically uploaded to PyPI by Gitlab CI on tag.

Bump the version with "-dev" in the develop branch
: - Make a branch like `bump-dev-version` from head of `develop`.
  - In `tango/release.py`, change `version_info`, e.g. from `(9, 4, 4)` to
    `(9, 4, 5, "dev", 0)`.
  - In `pyproject.toml`, change `version`, e.g. from `"9.4.4"` to
    `"9.4.5.dev0"`.
  - In `CMakeLists.txt`, change `VERSION`, e.g. from `9.4.4` to
    `9.4.5`.
  - Create MR, merge to `develop`.

Create and fill in the release description on GitLab
: - Go to the Tags page: <https://gitlab.com/tango-controls/pytango/-/tags>
  - Find the tag created above and click "Edit release notes".
  - Content must be the same as the details in the changelog.  List all the
    merge requests since the previous version.

Build conda packages
: - Conda-forge is used to build these. See <https://github.com/conda-forge/pytango-feedstock>
  - A new pull request should be created automatically by the Conda forge bot after our tag.
  - Get it merged by one of the maintainers.

Advertise the release on the mailing list
: - Post on the Python development list.
  - Example of a previous post:  <http://www.tango-controls.org/community/forum/c/development/python/pytango-921-release/>

Close off release issue
: - All the items on the check list should be ticked off by now.
  - Close the issue.

[autodoc]: https://pypi.python.org/pypi/autodoc
[myst]: https://myst-parser.readthedocs.io/
[pep8]: https://peps.python.org/pep-0008/
[pipx]: https://pypa.github.io/pipx/
[pixi]: https://pixi.sh
[pre-commit]: https://pre-commit.com
[restructuredtext]: http://docutils.sourceforge.net/rst.html
[ruff]: https://github.com/charliermarsh/ruff
[sphinx]: http://www.sphinx-doc.org/en/stable
[tutorial]: https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow
