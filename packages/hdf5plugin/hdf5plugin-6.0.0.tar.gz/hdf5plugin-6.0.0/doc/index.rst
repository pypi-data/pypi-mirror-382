hdf5plugin
==========

*hdf5plugin* provides `HDF5 compression filters <https://github.com/HDFGroup/hdf5_plugins/blob/master/docs/RegisteredFilterPlugins.md#list-of-filters-registered-with-the-hdf-group>`_ (namely: Blosc, Blosc2, BitShuffle, BZip2, FciDecomp, LZ4, Sperr, SZ, SZ3, Zfp, ZStd) and makes them usable from `h5py <https://www.h5py.org>`_.


* Supported operating systems: Linux, Windows, macOS.
* Supported versions of Python: >= 3.8
* Supported architectures: All.
  Specific optimizations are available for *x86* family, *arm64* and *ppc64le*.

*hdf5plugin* provides a generic way to enable the use of the provided HDF5 compression filters with `h5py` that can be installed via `pip` or `conda`.

Alternatives to install HDF5 compression filters are: system-wide installation on Linux or other conda packages: `blosc-hdf5-plugin <https://anaconda.org/conda-forge/blosc-hdf5-plugin>`_, `hdf5-lz4 <https://anaconda.org/nsls2forge/hdf5-lz4>`_.

:doc:`install`
    How-to install *hdf5plugin*

:doc:`usage`
    How-to use *hdf5plugin*

:doc:`information`
    Releases, changelog, repository, license

:doc:`contribute`
    How-to contribute to *hdf5plugin*

.. toctree::
   :hidden:

   install.rst
   usage.rst
   information.rst
   contribute.rst
   changelog.rst

:ref:`genindex`
