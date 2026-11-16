Release Notes
=============

.. towncrier release notes start

Unreleased
----------

Bugfixes
~~~~~~~~

- Handle oversized ``bytes`` and ``string`` lengths without leaking ``OverflowError``.
  Strict decoding raises ``InsufficientDataBytes`` for truncated data, while
  non-strict decoding continues to return the available data.

eth-abi v6.0.0-beta.1 (2025-12-17)
----------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Drop support for Python 3.8 & 3.9 (`#250 <https://github.com/ApeWorX/eth-abi/issues/250>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix typo in index (`#243 <https://github.com/ApeWorX/eth-abi/issues/243>`__)


Features
~~~~~~~~

- Add support for Python 3.14 (`#250 <https://github.com/ApeWorX/eth-abi/issues/250>`__)


eth-abi v5.2.0 (2025-01-14)
---------------------------

Features
~~~~~~~~

- Merge template, adding ``py313`` support, replace ``bumpversion`` with ``bump-my-version``, raise required ``hypothesis`` versions. (`#241 <https://github.com/ApeWorX/eth-abi/issues/241>`__)


Internal Changes - for eth-abi Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Merge template, fixing docs CI and other various updates (`#236 <https://github.com/ApeWorX/eth-abi/issues/236>`__)


eth-abi v5.1.0 (2024-04-01)
---------------------------

Internal Changes - for eth-abi Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Upgrade `parsimonious <https://github.com/erikrose/parsimonious>`_ from ``0.9`` to ``0.10``, which is 15% faster (`#231 <https://github.com/ApeWorX/eth-abi/issues/231>`__)
- Add ``python 3.12`` support, add all-format docs tests and nightly CI runs, reorg tests file structure to match CI grouping (`#232 <https://github.com/ApeWorX/eth-abi/issues/232>`__)


eth-abi v5.0.1 (2024-03-04)
---------------------------

Bugfixes
~~~~~~~~

- During decoding, verify all pointers in arrays and tuples point to a valid location in the payload (`#226 <https://github.com/ApeWorX/eth-abi/issues/226>`__)
- Fix memory leak warning in NodeVisitor and ABIRegistry (`#230 <https://github.com/ApeWorX/eth-abi/issues/230>`__)


Internal Changes - for eth-abi Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Clear mypy ``misc``-type errors and add top-level ``py.typed`` file back (`#221 <https://github.com/ApeWorX/eth-abi/issues/221>`__)


eth-abi v5.0.0 (2024-01-09)
---------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Drop python 3.7 support (`#217 <https://github.com/ApeWorX/eth-abi/issues/217>`__)


Internal Changes - for eth-abi Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Merge updates from the project template, notably, use ``pre-commit`` for linting and change the name of the ``master`` branch to ``main`` (`#217 <https://github.com/ApeWorX/eth-abi/issues/217>`__)
- Corrected format of booleans in ``pyproject.toml`` and added a test for the presence of the ``eth_abi.__version__`` attribute (`#219 <https://github.com/ApeWorX/eth-abi/issues/219>`__)


eth-abi v4.2.1 (2023-09-13)
---------------------------

Internal Changes - for eth-abi contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add ``build.os`` section to readthedocs build settings (`#213 <https://github.com/ApeWorX/eth-abi/issues/213>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#214 <https://github.com/ApeWorX/eth-abi/issues/214>`__


eth-abi v4.2.0 (2023-08-28)
---------------------------

Features
~~~~~~~~

- Allow turning off abi decoder "strict mode" when calling ``abi.decode()``. (`#198 <https://github.com/ApeWorX/eth-abi/issues/198>`__)


Bugfixes
~~~~~~~~

- Validate against zero-sized ``tuple`` types / empty Solidity structs. (`#212 <https://github.com/ApeWorX/eth-abi/issues/212>`__)


eth-abi v4.1.0 (2023-06-08)
---------------------------

Features
~~~~~~~~

- updated `StringDecoder` class to allow user-defined handling of malformed strings, handle with `strict` by default (`#187 <https://github.com/ApeWorX/eth-abi/issues/187>`__)


Internal Changes - for eth-abi contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- remove unused docs deps, bump version of remaining (`#203 <https://github.com/ApeWorX/eth-abi/issues/203>`__)
- Moved requirements-docs.txt info into .readthedocs.yml (`#204 <https://github.com/ApeWorX/eth-abi/issues/204>`__)
- pull in updates from the python project template (`#205 <https://github.com/ApeWorX/eth-abi/issues/205>`__)
- Updated CI process to handle tox issue caused by `virtualenv` update (`#208 <https://github.com/ApeWorX/eth-abi/issues/208>`__)


eth-abi v4.0.0 (2023-03-22)
---------------------------

No significant changes.


eth-abi v4.0.0-beta.3 (2023-03-20)
----------------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

- Upgrade Parsimonious dependency to allow >=0.9,<0.10 (`#201
  <https://github.com/ApeWorX/eth-abi/issues/201>`__)


eth-abi v4.0.0-beta.2 (2022-11-21)
----------------------------------

Features
~~~~~~~~

- Add support for Python 3.11 (`#194
  <https://github.com/ApeWorX/eth-abi/issues/194>`__)

Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#196 <https://github.com/ApeWorX/eth-abi/issues/196>`__


eth-abi v4.0.0-beta.1 (2022-09-27)
----------------------------------

Bugfixes
~~~~~~~~

- Reconcile differences in 32-byte padding between eth-abi encoders for dynamic
  types and Solidity's abi.encode() for 0 or empty values (`#158
  <https://github.com/ApeWorX/eth-abi/issues/158>`__)


Breaking Changes
~~~~~~~~~~~~~~~~

- Remove ``encode_abi_single()``, ``encode_packed_single()``, and
  ``decode_abi_single()``. Rename ``encode_abi()``, ``encode_abi_packed()``,
  and ``decode_abi()`` to ``encode()``, ``encode_packed()``, and ``decode()``,
  respectively. (`#161 <https://github.com/ApeWorX/eth-abi/issues/161>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#161 <https://github.com/ApeWorX/eth-abi/issues/161>`__, `#166
  <https://github.com/ApeWorX/eth-abi/issues/166>`__, `#167
  <https://github.com/ApeWorX/eth-abi/issues/167>`__, `#168
  <https://github.com/ApeWorX/eth-abi/issues/168>`__, `#177
  <https://github.com/ApeWorX/eth-abi/issues/177>`__, `#183
  <https://github.com/ApeWorX/eth-abi/issues/183>`__, `#186
  <https://github.com/ApeWorX/eth-abi/issues/186>`__


eth-abi v3.0.1 (2022-07-18)
---------------------------

Deprecations
~~~~~~~~~~~~

- Add ``DeprecationWarning`` for ``encode_abi()``, ``encode_single()``, ``decode_abi()``, and ``decode_single()`` and add temporary versions of ``abi.encode()`` and ``abi.decode()`` so users can start making these changes early. (`#165 <https://github.com/ApeWorX/eth-abi/issues/165>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#165 <https://github.com/ApeWorX/eth-abi/issues/165>`__, `#166 <https://github.com/ApeWorX/eth-abi/issues/166>`__, `#172 <https://github.com/ApeWorX/eth-abi/issues/172>`__, `#177 <https://github.com/ApeWorX/eth-abi/issues/177>`__, `#178 <https://github.com/ApeWorX/eth-abi/issues/178>`__


eth_abi 3.0.0 (2022-01-19)
--------------------------

Features
~~~~~~~~

- Add support for python 3.8 (`#145 <https://github.com/ApeWorX/eth-abi/issues/145>`__)
- Add support for Python 3.8. Includes updating mypy and flake8 version requirements (`#155 <https://github.com/ApeWorX/eth-abi/issues/155>`__)
- Drop Python 3.6 support, add Python 3.9 and 3.10 support. Update any dependencies accordingly (`#156 <https://github.com/ApeWorX/eth-abi/issues/156>`__)


Bugfixes
~~~~~~~~

- Catch ABITypeError exceptions when checking ``has_encoder`` (`#148 <https://github.com/ApeWorX/eth-abi/issues/148>`__)


Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Fix broken badges in README (`#144 <https://github.com/ApeWorX/eth-abi/issues/144>`__)


Miscellaneous changes
~~~~~~~~~~~~~~~~~~~~~

- `#123 <https://github.com/ApeWorX/eth-abi/issues/123>`__, `#154 <https://github.com/ApeWorX/eth-abi/issues/154>`__


eth-abi v2.1.1 (2020-02-27)
---------------------------

Bugfixes
~~~~~~~~

- If subclassing :meth:`eth_abi.decoding.ContextFramesBytesIO.seek`, the new method was not
  being used by :meth:`~eth_abi.decoding.ContextFramesBytesIO.seek_in_frame`. Now it will be. (`#139 <https://github.com/ApeWorX/eth-abi/issues/139>`__)


Internal Changes - for eth_abi contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Merged in project template, for changes in release scripts, docs, release notes, etc. (`#140 <https://github.com/ApeWorX/eth-abi/issues/140>`__)


v2.1.0
------

- Added support for "byte" alias for "bytes1" type.
- Added support for custom stream class in :class:`~eth_abi.codec.ABIDecoder`.
  See :ref:`custom_stream_class`.

v2.0.0
------

- Includes all changes from v2.0.0 beta and alpha versions.

v2.0.0-beta.9
-------------

- Added ``eth_abi.tools`` submodule with extra requirements installable with
  ``pip install eth-abi[tools]``.  See :ref:`tools`.

v2.0.0-beta.8
-------------

- Added  :meth:`~eth_abi.registry.ABIRegistry.has_encoder` and
  :meth:`~eth_abi.codec.ABIEncoder.is_encodable_type` to facilitate checking
  for type validity against coder registrations.

v2.0.0-beta.7
-------------

Released March 24, 2019

- Fixed an issue that caused custom types containing capital letters to be
  unparseable.
- Removed PyPy support.
- Added Python 3.7 support.

v2.0.0-beta.6
-------------

- Added the grammar module to the public API.  See :ref:`grammar`.
- Updated string API for the :class:`~eth_abi.grammar.ABIType`.  Type strings
  for :class:`~eth_abi.grammar.ABIType` instances are now obtained via the
  :meth:`~eth_abi.grammar.ABIType.to_type_str` method instead of by invoking
  the builtin Python ``str`` function with an instance of
  :class:`~eth_abi.grammar.ABIType`.

v2.0.0-beta.5
-------------

- Added registry copying functionality to facilitate modification of the
  default registry.  See :ref:`copying_an_existing_registry`.

v2.0.0-beta.4
-------------

- Update eth-typing requirement to ``>=2.0.0,<3.0.0``.

v2.0.0-beta.3
-------------

- Added codec API to facilitate use of custom registries.  See :ref:`codecs`.

v2.0.0-beta.2
-------------

Released October 16, 2018

- Bugfixes

  - Was accidentally allowing eth-typing v2. Now it requires eth-typing v1 only.

v2.0.0-beta.1
-------------

- New Features

  - Added support for nested dynamic arrays from the Solidity version 2 ABI
  - Added support for non-standard packed mode encoding
  - Added support for tuple array types e.g. ``(int,int)[]``
- Backwards Incompatible Changes

  - The :meth:`~eth_abi.abi.encode_single` and
    :meth:`~eth_abi.abi.decode_single` functions no longer accept type tuples
    to identify ABI types.  Only type strings are accepted.
  - The :meth:`~eth_abi.utils.parsing.collapse_type` function has been removed.
    People who still wish to use this function should replicate its logic
    locally and where needed.
  - The :meth:`~eth_abi.utils.parsing.process_type` function has been removed
    in favor of the :meth:`~eth_abi.grammar.parse` function.  This should make
    the parsing API more consistent with the new parsimonious parser.

v2.0.0-alpha.1
--------------

Released July 19, 2018

- Backwards Incompatible Changes

  - :meth:`~eth_abi.abi.decode_single` called with ABI type 'string' will now return a python
    :class:`str` instead of :class:`bytes`.
  - Support for the legacy ``real`` and ``ureal`` types has been removed
- Bugfixes

  - Simple callable encoders work again
- Misc

  - Various documentation updates and type annotations

v1.3.0
------

Released December 6, 2018

- Bugfixes

  - Resolved an issue that was preventing discovery of type hints.
- Misc

  - Updated eth-typing dependency version to ``>=2.0.0,<3.0.0``.

v1.2.2
-------------

Released October 18, 2018

- Bugfixes

  - Expand parsimonious dependency from v0.8.0 to v0.8.*

v1.2.1
------

Released October 16, 2018

- Bugfixes

  - Was accidentally allowing eth-typing v2. Now it requires eth-typing v1 only.
    (backport from v2)

v1.2.0
------

Released August 28, 2018

- New Features

  - Backported and added support for nested dynamic arrays from the Solidity
    version 2 ABI

v1.1.1
------

Released May 10, 2018

- Bugfixes

  - :meth:`~eth_abi.abi.is_encodable()` now returns ``False`` if a :class:`~decimal.Decimal` has
    too many digits to be encoded in the given ``fixed<M>x<N>`` type.
    (It was previously raising a :class:`ValueError`)
  - Raise an :class:`~eth_abi.exceptions.EncodingTypeError` instead of a
    :class:`TypeError` when trying to encode a :class:`float` into a ``fixed<M>x<N>`` type.

v1.1.0
------

Released May 8, 2018

- New Features

  - Added a Registry API (docs in progress) for looking up encoders by ABI type
  - Added support for types: tuple and fixedMxN
  - Added new is_encodable check for whether a value can be encoded with the given ABI type
- Bugfixes

  - Fix RealDecoder bug that allowed values other than 32 bytes
  - Fix bug that accepted ``stringN`` as a valid ABI type. Strings may not have a fixed length.
  - Stricter value checking when encoding a Decimal (Make sure it's not a NaN)
  - Fix typos in "missing property" exceptions
- Misc

  - Precompile regexes, for performance & clarity
  - Test fixups and switch to CircleCI
  - Readme improvements
  - Performance improvements
  - Drop Python 2 support cruft

v1.0.0
------

Released Feb 28, 2018

- Confirmed pypy3 compatibility
- Add support for eth-utils v1.0.0-beta2 and v1.0.1 stable
- Testing improvements

v1.0.0-beta.0
-------------

Released Feb 5, 2018

- Drop py2 support
- Add support for eth-utils v1-beta1

v0.5.0
------

- Rename to ``eth-abi`` for consistency across github/pypi/python-module

v0.4.4
------

- Better error messages for decoder errors.

v0.4.3
------

- Bugfix for ``process_type`` to support byte string type arrguments

v0.4.2
------

- ``process_type`` now auto-expands all types which have omittied their sizes.

v0.4.1
------

- Support for ``function`` types.

v0.3.1
------

- Bugfix for small signed integer and real encoding/decoding

v0.3.1
------

- Bugfix for faulty release.

v0.3.0
------

- Depart from the original pyethereum encoding/decoding logic.
- Fully rewritten encoder and decoder functionality.

v0.2.2
------

- Fix a handful of bytes encoding issues.

v0.2.1
------

- Use pyrlp utility functions for big_endian int operations

v0.2.0
------

- Bugfixes from upstream pyethereum repository for encoding/decoding
- Python 3 Support

v0.1.0
------

- Initial release
