.. _spkg_sirocco:

sirocco: Compute topologically certified root continuation of bivariate polynomials
===================================================================================

Description
-----------

sirocco is a library to compute topologically certified root
continuation of bivariate polynomials.

License
-------

GPLv3+


Upstream Contact
----------------

Miguel Marco (mmarco@unizar.es)

https://github.com/miguelmarco/SIROCCO2


Type
----

optional


Dependencies
------------

- :ref:`spkg_mpfr`

Version Information
-------------------

package-version.txt::

    2.1.0

See https://repology.org/project/sirocco/versions

Installation commands
---------------------

.. tab:: Sage distribution:

   .. CODE-BLOCK:: bash

       $ sage -i sirocco

.. tab:: Arch Linux:

   .. CODE-BLOCK:: bash

       $ sudo pacman -S sirocco

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install sirocco

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install sirocco sirocco-devel

.. tab:: openSUSE:

   .. CODE-BLOCK:: bash

       $ sudo zypper install sirocco-devel


However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
