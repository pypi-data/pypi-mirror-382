:py:mod:`simplemseed.seedcodec`
===============================

.. py:module:: simplemseed.seedcodec

.. autodoc2-docstring:: simplemseed.seedcodec
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`EncodedDataSegment <simplemseed.seedcodec.EncodedDataSegment>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.EncodedDataSegment
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`arrayTypecodeFromMSeed <simplemseed.seedcodec.arrayTypecodeFromMSeed>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.arrayTypecodeFromMSeed
          :summary:
   * - :py:obj:`canDecompress <simplemseed.seedcodec.canDecompress>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.canDecompress
          :summary:
   * - :py:obj:`decompress <simplemseed.seedcodec.decompress>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.decompress
          :summary:
   * - :py:obj:`encode <simplemseed.seedcodec.encode>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.encode
          :summary:
   * - :py:obj:`encodingName <simplemseed.seedcodec.encodingName>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.encodingName
          :summary:
   * - :py:obj:`getFloat64 <simplemseed.seedcodec.getFloat64>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.getFloat64
          :summary:
   * - :py:obj:`isFloatCompression <simplemseed.seedcodec.isFloatCompression>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.isFloatCompression
          :summary:
   * - :py:obj:`isPrimitiveCompression <simplemseed.seedcodec.isPrimitiveCompression>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.isPrimitiveCompression
          :summary:
   * - :py:obj:`mseed3EncodingFromArrayTypecode <simplemseed.seedcodec.mseed3EncodingFromArrayTypecode>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.mseed3EncodingFromArrayTypecode
          :summary:
   * - :py:obj:`mseed3EncodingFromNumpyDT <simplemseed.seedcodec.mseed3EncodingFromNumpyDT>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.mseed3EncodingFromNumpyDT
          :summary:
   * - :py:obj:`numpyDTFromMseed3Encoding <simplemseed.seedcodec.numpyDTFromMseed3Encoding>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.numpyDTFromMseed3Encoding
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`ASCII <simplemseed.seedcodec.ASCII>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.ASCII
          :summary:
   * - :py:obj:`BIG_ENDIAN <simplemseed.seedcodec.BIG_ENDIAN>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.BIG_ENDIAN
          :summary:
   * - :py:obj:`CDSN <simplemseed.seedcodec.CDSN>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.CDSN
          :summary:
   * - :py:obj:`DOUBLE <simplemseed.seedcodec.DOUBLE>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.DOUBLE
          :summary:
   * - :py:obj:`DWWSSN <simplemseed.seedcodec.DWWSSN>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.DWWSSN
          :summary:
   * - :py:obj:`FLOAT <simplemseed.seedcodec.FLOAT>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.FLOAT
          :summary:
   * - :py:obj:`INT24 <simplemseed.seedcodec.INT24>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.INT24
          :summary:
   * - :py:obj:`INTEGER <simplemseed.seedcodec.INTEGER>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.INTEGER
          :summary:
   * - :py:obj:`LITTLE_ENDIAN <simplemseed.seedcodec.LITTLE_ENDIAN>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.LITTLE_ENDIAN
          :summary:
   * - :py:obj:`SHORT <simplemseed.seedcodec.SHORT>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.SHORT
          :summary:
   * - :py:obj:`SRO <simplemseed.seedcodec.SRO>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.SRO
          :summary:
   * - :py:obj:`STEIM1 <simplemseed.seedcodec.STEIM1>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.STEIM1
          :summary:
   * - :py:obj:`STEIM2 <simplemseed.seedcodec.STEIM2>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.STEIM2
          :summary:
   * - :py:obj:`STEIM3 <simplemseed.seedcodec.STEIM3>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.STEIM3
          :summary:

API
~~~

.. py:data:: ASCII
   :canonical: simplemseed.seedcodec.ASCII
   :type: int
   :value: 0

   .. autodoc2-docstring:: simplemseed.seedcodec.ASCII

.. py:data:: BIG_ENDIAN
   :canonical: simplemseed.seedcodec.BIG_ENDIAN
   :value: 1

   .. autodoc2-docstring:: simplemseed.seedcodec.BIG_ENDIAN

.. py:data:: CDSN
   :canonical: simplemseed.seedcodec.CDSN
   :type: int
   :value: 16

   .. autodoc2-docstring:: simplemseed.seedcodec.CDSN

.. py:data:: DOUBLE
   :canonical: simplemseed.seedcodec.DOUBLE
   :type: int
   :value: 5

   .. autodoc2-docstring:: simplemseed.seedcodec.DOUBLE

.. py:data:: DWWSSN
   :canonical: simplemseed.seedcodec.DWWSSN
   :type: int
   :value: 32

   .. autodoc2-docstring:: simplemseed.seedcodec.DWWSSN

.. py:class:: EncodedDataSegment(compressionType, dataBytes: typing.Union[bytes, bytearray], numSamples, littleEndian: bool)
   :canonical: simplemseed.seedcodec.EncodedDataSegment

   .. autodoc2-docstring:: simplemseed.seedcodec.EncodedDataSegment

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.seedcodec.EncodedDataSegment.__init__

   .. py:attribute:: compressionType
      :canonical: simplemseed.seedcodec.EncodedDataSegment.compressionType
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.seedcodec.EncodedDataSegment.compressionType

   .. py:attribute:: dataBytes
      :canonical: simplemseed.seedcodec.EncodedDataSegment.dataBytes
      :type: typing.Union[bytes, bytearray]
      :value: None

      .. autodoc2-docstring:: simplemseed.seedcodec.EncodedDataSegment.dataBytes

   .. py:method:: decode()
      :canonical: simplemseed.seedcodec.EncodedDataSegment.decode

      .. autodoc2-docstring:: simplemseed.seedcodec.EncodedDataSegment.decode

   .. py:method:: isFloatCompression() -> bool
      :canonical: simplemseed.seedcodec.EncodedDataSegment.isFloatCompression

      .. autodoc2-docstring:: simplemseed.seedcodec.EncodedDataSegment.isFloatCompression

   .. py:attribute:: littleEndian
      :canonical: simplemseed.seedcodec.EncodedDataSegment.littleEndian
      :type: bool
      :value: None

      .. autodoc2-docstring:: simplemseed.seedcodec.EncodedDataSegment.littleEndian

   .. py:attribute:: numSamples
      :canonical: simplemseed.seedcodec.EncodedDataSegment.numSamples
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.seedcodec.EncodedDataSegment.numSamples

.. py:data:: FLOAT
   :canonical: simplemseed.seedcodec.FLOAT
   :type: int
   :value: 4

   .. autodoc2-docstring:: simplemseed.seedcodec.FLOAT

.. py:data:: INT24
   :canonical: simplemseed.seedcodec.INT24
   :type: int
   :value: 2

   .. autodoc2-docstring:: simplemseed.seedcodec.INT24

.. py:data:: INTEGER
   :canonical: simplemseed.seedcodec.INTEGER
   :type: int
   :value: 3

   .. autodoc2-docstring:: simplemseed.seedcodec.INTEGER

.. py:data:: LITTLE_ENDIAN
   :canonical: simplemseed.seedcodec.LITTLE_ENDIAN
   :value: 0

   .. autodoc2-docstring:: simplemseed.seedcodec.LITTLE_ENDIAN

.. py:data:: SHORT
   :canonical: simplemseed.seedcodec.SHORT
   :type: int
   :value: 1

   .. autodoc2-docstring:: simplemseed.seedcodec.SHORT

.. py:data:: SRO
   :canonical: simplemseed.seedcodec.SRO
   :type: int
   :value: 30

   .. autodoc2-docstring:: simplemseed.seedcodec.SRO

.. py:data:: STEIM1
   :canonical: simplemseed.seedcodec.STEIM1
   :type: int
   :value: 10

   .. autodoc2-docstring:: simplemseed.seedcodec.STEIM1

.. py:data:: STEIM2
   :canonical: simplemseed.seedcodec.STEIM2
   :type: int
   :value: 11

   .. autodoc2-docstring:: simplemseed.seedcodec.STEIM2

.. py:data:: STEIM3
   :canonical: simplemseed.seedcodec.STEIM3
   :type: int
   :value: 19

   .. autodoc2-docstring:: simplemseed.seedcodec.STEIM3

.. py:function:: arrayTypecodeFromMSeed(encoding: int) -> str
   :canonical: simplemseed.seedcodec.arrayTypecodeFromMSeed

   .. autodoc2-docstring:: simplemseed.seedcodec.arrayTypecodeFromMSeed

.. py:function:: canDecompress(encoding: int) -> bool
   :canonical: simplemseed.seedcodec.canDecompress

   .. autodoc2-docstring:: simplemseed.seedcodec.canDecompress

.. py:function:: decompress(compressionType: int, dataBytes: bytearray, numSamples: int, littleEndian: bool) -> numpy.ndarray
   :canonical: simplemseed.seedcodec.decompress

   .. autodoc2-docstring:: simplemseed.seedcodec.decompress

.. py:function:: encode(data, encoding=None, littleEndian=True)
   :canonical: simplemseed.seedcodec.encode

   .. autodoc2-docstring:: simplemseed.seedcodec.encode

.. py:function:: encodingName(encoding)
   :canonical: simplemseed.seedcodec.encodingName

   .. autodoc2-docstring:: simplemseed.seedcodec.encodingName

.. py:function:: getFloat64(dataBytes, offset, littleEndian)
   :canonical: simplemseed.seedcodec.getFloat64

   .. autodoc2-docstring:: simplemseed.seedcodec.getFloat64

.. py:function:: isFloatCompression(compressionType: int) -> bool
   :canonical: simplemseed.seedcodec.isFloatCompression

   .. autodoc2-docstring:: simplemseed.seedcodec.isFloatCompression

.. py:function:: isPrimitiveCompression(compressionType: int) -> bool
   :canonical: simplemseed.seedcodec.isPrimitiveCompression

   .. autodoc2-docstring:: simplemseed.seedcodec.isPrimitiveCompression

.. py:function:: mseed3EncodingFromArrayTypecode(typecode: str, itemsize: int) -> int
   :canonical: simplemseed.seedcodec.mseed3EncodingFromArrayTypecode

   .. autodoc2-docstring:: simplemseed.seedcodec.mseed3EncodingFromArrayTypecode

.. py:function:: mseed3EncodingFromNumpyDT(dt: numpy.dtype) -> int
   :canonical: simplemseed.seedcodec.mseed3EncodingFromNumpyDT

   .. autodoc2-docstring:: simplemseed.seedcodec.mseed3EncodingFromNumpyDT

.. py:function:: numpyDTFromMseed3Encoding(encoding: int)
   :canonical: simplemseed.seedcodec.numpyDTFromMseed3Encoding

   .. autodoc2-docstring:: simplemseed.seedcodec.numpyDTFromMseed3Encoding
