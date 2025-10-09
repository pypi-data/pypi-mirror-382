6.0.0: 08/10/2025
-----------------

This release requires Python >= 3.9 (PR #345).

- Compression filters and libraries:

  * Updated filter: **hdf5-blosc2** (PR #342)
  * Updated libraries:

    - **SPERR** (v0.8.4) (PR #356)
    - **snappy** (v1.2.2) (PR #353)
    - **c-blosc2** (v2.21.2) (PR #353)

  * Deprecated **SZ** filter (PR #352)

- Build:

  * Removed ``-ffast-math`` and ``/fp:fast`` compilation flags (PR #349)
  * Fixed build with system libraries on Windows (PR #339)
  * Moved embedded filters source code to a dedicated folder (PR #348)

* Deprecated ``hdf5plugin.version_info`` (PR #358)
* Added Python typing (PR #350, #360)
* Code formatting and linting (PR #340, #347)
* Updated project description and changelog (PR #344, #361)

5.1.0: 31/03/2025
-----------------

- Compression filters and libraries:

  * Updated **bitshuffle** filter (v0.5.2) (PR #334)
  * Updated **h5z-sperr** filter (v0.2.3) (PR #335, #336)
  * Updated **c-blosc2** compression library (v2.17.1) (PR #334, #337)

- Build:

  * Added ``HDF5PLUGIN_SYSTEM_LIBRARIES`` environment variable to build filters with system libraries (PR #333)
  * Fixed ``HDF5PLUGIN_STRIP=all`` environment variable to support missing folders (PR #331)

- Updated documentation (PR #323, #338)
- Updated continuous integration configuration (PR #331)

5.0.0: 30/08/2024
-----------------

This release requires Python >= 3.8 (PR #301) and h5py >= 3.0.0 (PR #300).

- Removed deprecated constants: ``hdf5plugin.config``, ``hdf5plugin.date``, ``hdf5plugin.hexversion`` and ``hdf5plugin.strictversion`` (PR #301)
- Compression filters and libraries:

  * Added **Sperr** filter (PR #303, #322)
  * Updated filters:

    - **Fcidecomp** (v2.1.1) (PR #311, #320)
    - **hdf5-blosc** (v1.0.1) (PR #310)
    - **LZ4** (commit 49e3b65) (PR #310)
    - **SZ** (commit f466775) (PR #310)

  * Updated libraries:

    - **c-blosc** (v1.21.6) (PR #320)
    - **c-blosc2** (v2.15.1) (PR #315, #320, #321)
    - **CharLS** (v2.1.0) (PR #311)
    - **LZ4** (v1.10.0) (PR #320)
    - **Snappy** (v1.2.1) (PR #310)
    - **zlib** (v1.3.1) (PR #320)
    - **ZStd** (v1.5.6) (PR #315)

  * Fixed **zfp** compilation options for Visual Studio 2022 (PR #313)

- Fixed ``hdf5plugin.Bitshuffle`` to avoid raising ``ValueError`` when ``lz4=False`` (PR #309)
- Fixed compilation warning on Windows by removing ``/openmp`` link flags (PR #316)
- Added ``HDF5PLUGIN_CPP20`` build configuration environment variables for **Sperr** (PR #303)
- Updated ``setup.py`` (PR #298)
- Updated copyright statement (PR #308)
- Updated documentation (PR #299, #312, #314, #319)
- Updated continuous integration configuration (PR #298, #312,#313, #314)

4.4.0: 08/02/2024
-----------------

- **blosc2** filter: Added support of `blosc2 plugins <https://www.blosc.org/posts/dynamic-plugins/>`_ (PR #295)
- **SZ3** filter: Updated tests and documentation (PR #290, #296)
- Updated **c-blosc2** (v2.13.2) (PR #287, #291, #293, #295)
- Updated **zfp** (v1.0.1) (PR #287)

- Added automated release workflow (PR #292, #294)
- Updated documentation (PR #285, #288, #297)

4.3.0: 09/11/2023
-----------------

- Updated **hdf5-blosc2** to support b2nd (PR #282)
- Updated **c-blosc2** (v2.11.1) and enabled its AVX512 support (PR #283)

- Updated continuous integration to test with Python 3.12 (PR #281)
- Added European HDF Users Group (HUG) Meeting 2023 presentation and companion material (PR #280)
- Updated documentation (PR #279, #284)

4.2.0: 12/09/2023
-----------------

- Updated libraries: **c-blosc** (v1.12.5), **c-blosc2** (v2.10.2) (PR #273)
- Updated filter **H5Z-ZFP** (v1.1.1) (PR #273)

- Updated build dependencies:

  * Added `wheel`>=0.34.0 requirement (PR #272)
  * Removed `distutils` usage (PR #276)

- Updated documentation (PR #271, #278)
- Fixed Continuous integration (PR #275)
- Debian packaging (PR #277):

  * Added Debian 12
  * Removed Debian 10

4.1.3: 16/06/2023
-----------------

This is a bug fix release:

- Fixed **SZ** compression filter build option that was leading to errors higher than the required tolerance (PR #268, #269)

4.1.2: 01/06/2023
-----------------

- Updated libraries: **c-blosc** (v1.12.4), **c-blosc2** (v2.9.2), snappy (v1.1.10) **zstd** (v1.5.5), **zlib** (v1.2.13) (PR #266)
- Updated filter registration (PR #264)

4.1.1: 23/01/2023
-----------------

This is a bug fix release:

- Fixed **c-blosc2** compilation on ARM architecture (PR #262)
- Updated continuous integration tests (PR #261)

4.1.0: 17/01/2023
-----------------

This version of ``hdf5plugin`` provides 2 new filters: **Blosc2** and **SZ3**.

- New compression filters:

  * Added **SZ3** filter (PR #224, #241, #242, #243, #246)
  * Added **Blosc2** filter (PR #201, #249, #253, #255)

- Updated filters:

  * Updated **bitshuffle** (v0.5.1) (PR #251)
  * Updated **c-blosc** (v1.21.2) and **LZ4** compression library (v1.9.4) (PR #250)

- Build:

  * Added build configuration environment variables:

    * ``HDF5PLUGIN_CPP14`` for SZ3 (PR #242)
    * ``HDF5PLUGIN_BMI2`` for Zstd compression library (PR #247)
    * ``HDF5PLUGIN_INTEL_IPP_DIR`` for Blosc2 filter and LZ4 compression library (PR #252)

  * Added Intel IPP optional support for LZ4 compression (PR #252)
  * Refactored build (PR #233, #240, #248, #255, #257)

- Misc.:

  * Updated documentation (PR #256, #259)

4.0.1: 2022/12/06
-----------------

This is a bug-fix release:

- Updated embedded version of `SZ` to fix a compression issue under Windows (PR #231)
- Updated tests to pass with older versions of `bitshuffle` (PR #235)
- Improved HDF5 function wrapper (PR #228)
- Fixed and updated documentation (PR #223, #232, #238)

4.0.0: 2022/11/28
-----------------

This version of ``hdf5plugin`` requires at least Python >= v3.7 (PR #210).

While the provided plugin filters are backwards compatible, this version includes an updated version of the H5Z-ZFP filter (v1.1.0). This version of the filter can read data compressed by previous versions but newly ZFP-compressed data cannot be read by older versions (PR #190). 

- New compression filters:

  * Added **SZ** filter (PR #203, #206, #209, #213, #215)
  * Added **BZip2** filter (PR #182)

- New functions:

  * Added **get_config()** function to retrieve build information and currently registered filters (PR #187)
  * Added **get_filters()** function to retrieve selected compression filter helper class (PR #212)
  * Added **register()** function to force registration of provided filters (PR #208, #212)

- Deprecations:

  * ``Bitshuffle``'s ``lz4`` argument: Use ``cname`` argument instead (PR #171)
  * ``config``: use ``get_config()`` function instead (PR #210)
  * ``date``, ``hexversion`` and ``strictversion`` (PR #217)

- Updated filters:

  * Updated ``snappy`` library to v1.1.9 (used by the ``blosc`` filter) (PR #192)
  * Updated ``Zfp`` filter to HZ5-ZFP v1.1.0 and ZFP v1.0.0 (PR #190)
  * Updated ``Bitshuffle`` filter to v0.4.2 (PR #171)
  * Updated ``c-blosc`` to commit 9dc93b1 and ``zstd`` to v1.5.2 (PR #200)

- Build:

  * Updated ``HDF5PLUGIN_STRIP`` environment variable behaviour and added support for ``"all"`` value (PR #188)
  * Added optimisation flags for the ``blosc`` filter compilation (PR #180)
  * Added check of native flags availability (PR #189)

- Misc.:

  * Updated project to use Python >3.7 (PR #210)
  * Code reorganisation, clean-up, code style (PR #191, #205, #217)
  * Updated documentation (PR #184, #196, #199, #211, #218)
  * Updated continuous integration tests (PR #198)

3.3.1: 2022/06/03
-----------------

- Fixed LZ4 filter compilation with `HDF5PLUGIN_HDF5_DIR` (PR #178)
- Renamed `PLUGINS_PATH` constant to `PLUGIN_PATH` without `S` (PR #179)
- Added notebook of European HUG meeting 2022 (PR #176)
- Updated changelog and version (PR #181)

3.3.0: 2022/05/25
-----------------

- Deprecated build options passed as arguments to `setup.py`, use environment variables instead (PR #167)
- Updated LZ4 filter to latest available code and LZ4 compression v1.9.3 (PR #172)
- Added `clevel` argument to `Zstd` (PR #164)
- Added `config.embedded_filters` to advertise embedded filters, and `HDF5PLUGIN_STRIP` to configure it during the build (PR #169)
- Added `-v` option to `python -m hdf5plugin.test` (PR #166)
- Changed "filter already loaded, skip it." log message from warning to info (PR #168)
- Updated build, now using `pyproject.toml` (PR #167, #173)
- Updated changelog and version (PR #174)

3.2.0: 2021/10/15
-----------------

- Updated libraries: blosc v1.21.1 (lz4 v1.9.3, zlib v1.2.11, zstd v1.5.0), snappy v1.1.8 (PR #152, #156)
- Fixed compilation issue occuring on ppc64le in conda-forge (PR #154)
- Documentation: Added European HDF User Group presentation (PR #150) and updated changelog (PR #155)

3.1.1: 2021/07/07
-----------------

This is a bug fix release:

- Fixed `hdf5plugin` when installed as a Debian/Ubuntu package (PR #147)
- Fixed and updated documentation (PR #143, #148)

3.1.0: 2021/07/02
-----------------

This version of `hdf5plugin` requires Python3 adds `mips64` supports and improves support for other architectures.

- Added support of `mips64` architecture (PR #126)
- Added enhanced documentation based on sphinx hosted at http://www.silx.org/doc/hdf5plugin/latest/ and on readthedocs.org (PR #137, #139, #141)
- Fixed LZ4 filter by downgrading used lz4 algorithm implementation (PR #123)
- Fixed `python setup.py install` (PR #125, #130)
- Improved build options support (PR #125, #130, #135, #140)
- Improved tests (PR #128, #129, #132)
- Cleaned-up python2 compatibility code (PR #134)
- Updated project description/metadata: Added Python3.9, `python_requires`, updated status to "Stable" (PR #119, #127, #138)
- Updated CHANGELOG and version (PR #142)

3.0.0
-----

This version of `hdf5plugin` requires Python3 and supports arm64 architecture.

- Stopped Python2.7 support (PR #104, #105)
- Added support of arm64 architecture (PR #116)
- Added `Zstd` filter to the supported plugin list (PR #106)
- Added `hdf5plugin.config` to retrieve build options at runtime (PR #113)
- Added support of build configuration through environment variables (PR #116)
- Fixed `FciDecomp` error message when built without c++11 (PR #113)
- Updated blosc compile flags (`-std-c99`) to build for manylinux1 (PR #109)
- Updated c-blosc to v1.20.1 (PR #101)
- Updated: continuous integration (PR #104, #111), project structure (PR #114, #118), changelog (PR #117)

2.3.2
-----

This is the last version of `hdf5plugin` supporting Python 2.7.

- Enabled SIMD on power9 for bitshuffle filter (PR #90)
- Added github actions continous intergration (PR #99)
- Added debian/ubuntu packaging support (PR #87)
- Fixed compilation under macos10.15 with Python 3.8 (PR #102)
- Fixed `numpy` 1.20 deprecation warning (PR #97)
- Updated CHANGELOG and version (PR #91, #103)

2.3.1
-----

- Fixed support of wheel package version >= 0.35 (PR #82)
- Fixed typo in error log (PR #81)
- Continuous integration: Added check of package description (PR #80)
- Fixed handling of version info (PR #84)

2.3
---

- Added ZFP filter (PR #74, #77)
- Updated README (PR #76, #79)

2.2
---

- Added FCIDECOMP filter (PR #68, #71)

2.1.2
-----

- Fixed OpenMP compilation flag (PR #64)
- Fixed support of `wheel` package version >= 0.34 (PR #64)
- Continuous Integration: Run tests with python3 on macOS rather than python2. (PR #66)

2.1.1
-----

- Fixed `--native` build option on platform other than x86_64 (PR #62)
- Fixed build of the snappy C++11 library for blosc on macOS (PR #60)

2.1.0
-----

- Added `--openmp=[False|True]` build option to compile bitshuffle filter with OpenMP. (PR #51)
- Added `--sse2=[True|False]` build option to compile blosc and bitshuffle filters with SSE2 instructions if available. (PR #52)
- Added `--avx2=[True|False]` build option to compile blosc and bitshuffle filters with AVX2 instructions if available. (PR #52)
- Added `--native=[True|False]` build option to compile filters for native CPU architecture. This enables SSE2/AVX2 support for the bitshuffle filter if available. (PR #52)
- Added snappy compression to the blosc filter if C++11 is available (`--cpp11=[True|False]` build option). (PR #54)
- Improved wheel generation by using root_is_pure=True setting. (PR #49)

2.0.0
-----

- Added compression support for Linux and macOS
- Added blosc filter
- Added helper class (Blosc, Bitshuffle and LZ4) to ease providing compression arguments to h5py
- Added tests
- Updated documentation
- Building from source through setup.py
- No longer use the plugin mechanism via HDF5_PLUGIN_PATH environment variable

1.4.1
-----

- Support Python 3.7 under 64-bit windows

1.4.0
-----

- Manylinux support

1.3.1
-----

- Support Python 3.6 under 64-bit windows.

1.3.0
-----

- Add 64-bit manylinux version LZ4 filter plugin

- Add 64-bit manylinux version bitshuffle plugin

- Implement continuous imtegration testing


1.2.0
-----

- Add LZ4 filter plugin for MacOS

- Add bitshuffle plugin decompressor for MacOS

1.1.0
-----

- Add bitshuffle plugin.

- Document origin and license of the used sources.

1.0.1
-----

- Replace corrupted VS2015 64 bit dll.

1.0.0
-----

- Initial release with LZ4 filter plugin.
