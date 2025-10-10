Make a new release
==================

Install tools
-------------

::

   pip install -r build_requirements.txt

Prepare a new release
---------------------

1. Commit all changes.

2. Bump version up with:

   ::

      bumpversion patch

   or

   ::

      bumpversion minor
   or

   ::

      bumpversion major


3. Build new ``.tar.gz`` and ``.whl`` files in ``/dist`` with:

   ::

      python3 -m build

4. Test-upload to https://test.pypi.org:

   ::

      python3 -m twine upload --repository testpypi dist/*

   Check the upload on https://test.pypi.org

5. If test-upload is ok, then make actual upload to https://pypi.org:

   ::

      python3 -m twine upload dist/*

Further information
-------------------

https://packaging.python.org/tutorials/packaging-projects/#uploading-your-project-to-pypi
