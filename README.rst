================================================
PROVED (PRocess mining OVer uncErtain Data)
================================================


The PROVED (PRocess mining OVer uncErtain Data) app is a tool that enables process mining analysis on uncertain event data. It is a Django web application interfacing with the homonym library (proved-core).


* Free software: GNU General Public License v3
* Documentation: https://provedapp.readthedocs.io (Coming soon).


Features
--------

* Upload and download of uncertain event logs
* Uncertain data explorer
* Conformance checking through alignments on uncertain event data


Installation
------------

PROVED is a Django application compatible with Python 3.6+. Download the repository, enter the main folder and type

``pip install proved``

to install the requirements from PyPi.

The application can be started with

``python manage.py runserver``

the application will start on the port 8000, and will be accessible from any web browser.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
