Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.


Version 1.4.3 (2025/10/09)
--------------------------

* Added: support for Python 3.14
* Removed: support for Python 3.9


Version 1.4.2 (2025/06/11)
--------------------------

* Added: support for Python 3.13


Version 1.4.1 (2024/06/18)
--------------------------

* Added: support for ``numpy`` 2.0
* Removed: support for Python 3.8


Version 1.4.0 (2023/10/05)
--------------------------

* Added: ``audmath.similarity()``
* Added: support for Python 3.12


Version 1.3.0 (2023/07/10)
--------------------------

* Added: ``audmath.samples()``
* Removed: support for Python 3.7


Version 1.2.1 (2022/02/07)
--------------------------

* Added: support for
  ``None``,
  ``''``,
  ``'None'``,
  ``'NaN'``,
  ``'NaT'``,
  ``np.NaN``,
  ``pd.NA``,
  ``pd.NaT``
  to represent ``NaN``
  in ``audmath.duration_in_seconds()``
* Added: support for ``'Inf'``, ``'-Inf'``, ``np.inf``, ``-np.inf``
  to represent ``Inf``, ``-Inf``
  in ``audmath.duration_in_seconds()``
* Fixed: sign support in string values
  (``'-1 ms'``, ``'+s'``)
  in ``audmath.duration_in_seconds()``


Version 1.2.0 (2022/02/01)
--------------------------

* Added: ``audmath.duration_in_seconds()``
  to convert any duration value to seconds


Version 1.1.1 (2022/12/20)
--------------------------

* Added: support for Python 3.11
* Changed: split API documentation into sub-pages
  for each function


Version 1.1.0 (2022/12/02)
--------------------------

* Added: ``audmath.rms()``
  to calculate root mean square of signal
* Added: ``audmath.db()``
  to convert from amplitude to decibel
* Added: ``audmath.invert_db()``
  to convert from decibel to amplitude
* Added: ``audmath.window()``
  to provide different kind
  of (half-)windows 
* Added: support for Python 3.10


Version 1.0.0 (2022/01/03)
--------------------------

* Added: Python 3.9 support
* Removed: Python 3.6 support


Version 0.9.4 (2021/10/25)
--------------------------

* Fixed: bottom margin in API table


Version 0.9.3 (2021/10/25)
--------------------------

* Changed: use new ``sphinx-audeering-theme``


Version 0.9.2 (2021/07/30)
--------------------------

* Fixed: package name in installation docs


Version 0.9.1 (2021/07/29)
--------------------------

* Added: benchmarks for ``audmath.inverse_normal_distribution()``
  against ``scipy``
* Changed: implement ``audmath.inverse_normal_distribution()``
  in a native vectorized way
* Fixed: missing links in changelog


Version 0.9.0 (2021/07/28)
--------------------------

* Added: Initial release
* Added: ``audmath.inverse_normal_distribution()``


.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html
