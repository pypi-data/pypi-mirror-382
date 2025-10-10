.. _contributing:

Contributing to HerosDevices
############################

We welcome contributions from everyone, the HEROS devices library lives from community contributions to support
a large quantity of scientific devices! Whether you're new to coding or you are an experienced contributor, this guide will help you get started.

Ways to Contribute
******************
There are many ways to contribute, regardless of your experience level:

Reporting issues
===============

Found a bug? Have an idea for a new feature? Reporting issues is one of the most valuable ways to contribute as it helps us improve the project.
Head over to the `issue page on our GitLab <https://gitlab.com/atomiq-project/herosdevices/-/issues>`_.

When adding new issues, try to adhere to the following principles:

- Check existing issues to avoid duplicates
- Provide clear, reproducible steps for bugs
- Include relevant information (OS, Python version, etc.)

Writing tutorials and improving documentation
=============================================

Help new users get started by creating tutorials and improving the documentation.
This is an invaluable way to contribute if you are fairly new to the project or non-coding experienced
as it is always hard to capture all the pitfalls and steps if you are experienced with the project and
everything is clear to you.

If you find anything where the documentation is lacking, please consider improving it or creating an issue.
Also small contributions like fixing typos or layout issues are always more than welcome!

There is typically also a range of documentation related issues `on our GitLab <https://gitlab.com/atomiq-project/herosdevices/-/issues?label_name%5B%5D=documentation>`_.

Fixing bugs and adding features
===============================

Community contributions in the form of new features or bug fixes are highly appreciated.
For many device drivers it is actually necessary to own the physical hardware. As the maintainers can not own each and every device,
contributing device drivers and fixing driver related issues is an extremely important and valued task.

If you looking into fixing an issue, don't hesitate to ask for clarification if you're unsure about requirements.
Keep your fixes minimal and focused without changing large parts of the codebase. Also consider writing tests that reproduce the bug
and help avoiding it in the future.

When implementing features, start by opening an `issue <https://gitlab.com/atomiq-project/herosdevices/issues>`_ with your proposal so it can be discussed by the community.
Again, try to focus on one manageable feature and keep the code changes as simple as possible. Please follow the existing code patterns and conventions. The best starting point
is always to look at existing code and getting familiar with it. For your code to be really usable by a broad public it needs to be lined with documentation and comprehensive tests.

And most importantly, if you don't feel comfortable with a certain sub task, don't hesitate to ask for help (for example in our `matrix channel <https://matrix.to/#/#atomiq:matrix.org>`_)!

|


Making Changes to the Codebase
******************************

If you want to contribute directly to the codebase, either by writing documentation, fixing bugs or contributing device drivers, this is the section for you.
It assumes a basic understanding of Git and GitLab, if you are new to that, consider reading `GitLabs official guide <https://docs.gitlab.com/topics/git/get_started/>`_.

Setting up the development environment
======================================

Before you begin contributing code or documentation, you'll need to set up your development environment. Here's what you'll need:

- **GitLab account**: Required to contribute code. `Sign up here <https://gitlab.com/>`_ if you don't have one.
- **uv**: Our preferred Python virtual environment manager. `Installation instructions <https://docs.astral.sh/uv/getting-started/installation/>`_. But you can also use any other way to create and use virtual environments.

**Fork and clone the repository**
   Create your own copy of the repository by clicking the **Fork** button on our `GitLab page <https://gitlab.com/atomiq-project/herosdevices>`_.
   This allows you to freely experiment with changes without affecting the main project. Once forked, clone your fork to your local machine by running

   .. code-block:: console

      git clone https://gitlab.com/<your-username>/herosdevices.git
      cd herosdevices


**Install dependencies**
   Create a virtual environment in your repository folder by running:

   .. code-block:: console

      uv venv

   To Install the necessary python dependencies, run:

   .. code-block:: console

      uv pip install -e ".[dev,docs]"

   This installs the package in editable mode along with all development and documentation dependencies.

   .. important::
     As the repository uses many different vendor libraries, depending on what you want to contribute, you may have to install the corresponding packages.
     Refer to the documentation of the individual drivers for more details.

**Create a descriptive Branch**
  Start your development on a branch :ref:`describing your code change <contrib-branches>` by running

  .. code-block:: console

    git checkout -b <your-branch>


Implement, Test and Document your Changes
=========================================

.. important::
  Before implementing, read the :ref:`contrib-code-guide` and prepare your environment accordingly.

After applying your changes, run our tests by running

.. code-block:: console

    uv run pytest

If the existing tests fail, adjust your code so that they pass or start a discussion in your merge request (see below) why the tests should be changed.

.. important::
  If you added new feature, consider writing new tests to validate their functionality and :ref:`add documentation! <contrib-write-doc>`


Commit and push
===============

When you're ready to contribute your changes, commit them and push them to your GitLab fork by running:

.. code-block:: console

    git add path/to/modified/files
    git commit -m "Commit message describing your changes"
    git push --set-upstream origin <your-branch>


Submit a merge request
======================

Finally, initiate a pull request to merge your contributions with the main repository.
From the main repository page, go to the `Merge requests <https://gitlab.com/atomiq-project/herosdevices/-/merge_requests>`_ page, and click the `New merge request` button and select your fork and branch as a source.
Compare your branches and write a comprehensive description of the changes you made, use one of the predefined templates to guide you through.

Then submit the request and wait for the maintainers to check, comment and approve your code.

|


.. _contrib-branches:

Working with branches
*********************

We use a simple branching model to manage development:

- The ``main`` branch contains production-ready code and is protected from direct pushes
- All development happens in feature branches that are merged via merge requests. **Do not edit the** ``main`` **branch directly as it makes it much harder to keep your fork up to date with upstream**
- Feature branches should be created from the latest ``main`` branch

When creating branches, please use these naming conventions:

- ``device/<device-name>`` for new device drivers (e.g., ``device/siglent-sdg6xxx``)
- ``feat/<short-description>`` for new features (e.g., ``feat/onewire-bus``)
- ``fix/<short-description>`` for bug fixes (e.g., ``fix/pvcam-init``)
- ``doc/<short-description>`` for documentation changes (e.g., ``doc/update-install-guide``)
- ``test/<short-description>`` for testing improvements (e.g., ``test/add-coverage-for-camera``)

To ensure you're working with the latest code, use the `Update Fork` button on the GitLab page of your fork!
This helps prevent merge conflicts and keeps your development environment in sync with the main project.

.. _contrib-code-guide:

Coding Guidelines
*****************

We recommend that you use the following tools for linting and formatting:

`Pre-commit <https://pre-commit.com/>`_ tool
  Once you've installed this tool, integrate it as a pre-commit hook into your local repository with the following command:

  .. code-block:: console

    pre-commit install

  This automatically formats your code and conducts style checks before each commit. For manual checks at any time, execute:

  .. code-block:: console

    pre-commit run --all-files

`Ruff <https://docs.astral.sh/ruff/>`_
    Installing `ruff` into the editor of your choice helps you with adhering to the style guide of this project directly while your write your code!
    See this `guide <https://docs.astral.sh/ruff/editors/setup/>`_ on how to integrate `ruff` in your editor.

`Mypy <https://mypy-lang.org/>`_
  MyPy helps you with getting the types right. It is run in the GitLab-CI but it helps running it before committing to avoid trial and error committing.
  Run MyPy on all files

  .. code-block:: console

    uv run mypy src/

  Or on a single file:

  .. code-block:: console

    uv run mypy src/herosdevices/helper.py

  .. note::

    Note that currently not all drivers are typed correctly, so MyPy will show a lot of errors. We recommend running it just on the files you changed.


.. _contrib-write-doc:

Writing documentation
*********************

Good documentation is essential for making the project accessible:
We are using `Google format <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_ for docstrings of all public functions and classes.
We recommend reading the Google `doc style guide <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_ for a tutorial on how to write good docstrings.

If you added a new device driver, make sure to include an example how to setup the device with a `boss <https://boss-eb4966.gitlab.io/json.html>`_ JSON string.
An example for this kind of docstring can be found in the `PvcamCamera class <https://gitlab.com/atomiq-project/herosdevices/-/blob/main/src/herosdevices/hardware/teledyne/pvcam.py>`_.

.. _contrib-build-doc:

Building Documentation Locally
==============================

When making changes to the documentation, it is often necessary to visually check the result, therefore you have to build it locally.
Our documentation is built using Sphinx, to build it run:

.. code-block:: console

  uv run --directory docs/ make html

View the documentation by opening ``./build/html/index.html`` in your browser.
