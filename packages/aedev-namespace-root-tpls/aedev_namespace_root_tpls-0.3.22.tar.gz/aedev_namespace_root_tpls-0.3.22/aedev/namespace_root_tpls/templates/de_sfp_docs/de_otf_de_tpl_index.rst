namespace portions documentation
################################

welcome to the documentation of the portions (modules and packages) of this freely extendable
**{namespace_name}** namespace (:pep:`420`).


.. include:: features_and_examples.rst


code maintenance guidelines
***************************


portions code features
======================

    * open source
    * pure python
    * fully typed (:pep:`526`)
    * fully :ref:`documented <{namespace_name}-portions>`
    * 100 % test coverage
    * multi thread save
    * code checks (using pylint and flake8)


design pattern and software principles
======================================

    * `DRY - don't repeat yourself <http://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`__
    * `KIS - keep it simple <http://en.wikipedia.org/wiki/Keep_it_simple_stupid>`__


.. include:: ../CONTRIBUTING.rst


create new namespace
====================

a :pep:`420` namespace splits the codebase of a library or framework into multiple project repositories, called
portions (of the namespace).

.. hint::
    the `aedev` namespace is providing `the project-manager (pjm) tool to create and maintain namespace root
    and its portion projects <https://aedev.readthedocs.io/en/latest/man/project_manager.html>`__.

the id of a new namespace has to be available on `PyPI <pypi.org>`__.

the owner name of your namespace (group-name) has to be available on your git repository server. it defaults
to the namespace name plus the suffix ``'-group'``.


register a new namespace portion
================================

follow the steps underneath to add and register a new module portion onto the **{namespace_name}** namespace:

1. open a console window and change the current directory to the parent directory of your projects root folders.
2. choose a not-existing/unique name for the new portion (referred as `<portion-name>` in the next steps).
3. run ``pjm --namespace_name={namespace_name} --project_name={namespace_name}_<portion_name> new_module``
   to create a new project folder `{namespace_name}_<portion-name>`,
   and to register the portion name within the namespace.
4. run ``cd {namespace_name}_<portion-name>`` to change the current to the working tree root
   of the new portion project. within the project folder you will find the
   initial project files created from templates and a pre-configured git repository (with the remote
   already set and the initial files unstaged, to be extended, staged and finally committed).
5. optionally run `pyenv local venv_name <https://pypi.org/project/pyenv/>`__ (or any other similar tool) to
   create/prepare a local virtual environment.
6. fans of TDD are then coding unit tests in the prepared test module `test_{namespace_name}_<portion-name>{PY_EXT}`,
   situated within the `{TESTS_FOLDER}` sub-folder of your new code project folder.
7. extend the file <portion_name>{PY_EXT} situated in the `{namespace_name}` sub-folder to implement the new portion.
8. run ``pjm check-integrity`` to run the linting and unit tests (if they fail go one or two steps back).
9. run ``pjm prepare``, then amend the commit message within the file `{COMMIT_MSG_FILE_NAME}` and run ``pjm commit``.

the registration of a new portion to the **{namespace_name}** namespace has to be done by a namespace maintainer.
if you have a maintainer role in the namespace owner group `{repo_group}` (at {repo_root}) then you can push and
merge the new portion directly (running ``pjm push`` and ``pjm request``). otherwise contact one of the maintainers
to add it for you.

registered portions will automatically be included into the `{namespace_name} namespace documentation`, available at
`ReadTheDocs <{docs_root}>`__.



.. _{namespace_name}-portions:

registered namespace package portions
*************************************

the following list contains all registered portions of the **{namespace_name}** namespace, plus additional modules
of each portion.


.. hint::
    a not on the ordering: portions with no dependencies are at the begin of the following list.
    the portions that are depending on other portions of the **{namespace_name}** namespace
    are listed more to the end.


.. autosummary::
    :toctree: _autosummary
    :nosignatures:

    {portions_import_names}


{manuals_include}


indices and tables
******************

* `portion repositories at {repo_domain} <{repo_root}>`__
* :ref:`genindex`
* :ref:`modindex`
* ``ae`` namespace `projects <https://gitlab.com/ae-group>`__ and `documentation <https://ae.readthedocs.io>`__
* ``aedev`` namespace `projects <https://gitlab.com/aedev-group>`__ and `documentation <https://aedev.readthedocs.io>`__
