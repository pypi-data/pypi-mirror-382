:py:mod:`simplemseed.steim1`
============================

.. py:module:: simplemseed.steim1

.. autodoc2-docstring:: simplemseed.steim1
   :allowtitles:

Module Contents
---------------

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`decodeSteim1 <simplemseed.steim1.decodeSteim1>`
     - .. autodoc2-docstring:: simplemseed.steim1.decodeSteim1
          :summary:
   * - :py:obj:`encodeSteim1 <simplemseed.steim1.encodeSteim1>`
     - .. autodoc2-docstring:: simplemseed.steim1.encodeSteim1
          :summary:
   * - :py:obj:`encodeSteim1FrameBlock <simplemseed.steim1.encodeSteim1FrameBlock>`
     - .. autodoc2-docstring:: simplemseed.steim1.encodeSteim1FrameBlock
          :summary:
   * - :py:obj:`extractSteim1Samples <simplemseed.steim1.extractSteim1Samples>`
     - .. autodoc2-docstring:: simplemseed.steim1.extractSteim1Samples
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`ONE_BYTE <simplemseed.steim1.ONE_BYTE>`
     - .. autodoc2-docstring:: simplemseed.steim1.ONE_BYTE
          :summary:
   * - :py:obj:`TWO_BITS <simplemseed.steim1.TWO_BITS>`
     - .. autodoc2-docstring:: simplemseed.steim1.TWO_BITS
          :summary:
   * - :py:obj:`TWO_BYTE <simplemseed.steim1.TWO_BYTE>`
     - .. autodoc2-docstring:: simplemseed.steim1.TWO_BYTE
          :summary:

API
~~~

.. py:data:: ONE_BYTE
   :canonical: simplemseed.steim1.ONE_BYTE
   :value: 'int32(...)'

   .. autodoc2-docstring:: simplemseed.steim1.ONE_BYTE

.. py:data:: TWO_BITS
   :canonical: simplemseed.steim1.TWO_BITS
   :value: 'int32(...)'

   .. autodoc2-docstring:: simplemseed.steim1.TWO_BITS

.. py:data:: TWO_BYTE
   :canonical: simplemseed.steim1.TWO_BYTE
   :value: 'int32(...)'

   .. autodoc2-docstring:: simplemseed.steim1.TWO_BYTE

.. py:function:: decodeSteim1(dataBytes: bytearray, numSamples, bias=np.int32(0))
   :canonical: simplemseed.steim1.decodeSteim1

   .. autodoc2-docstring:: simplemseed.steim1.decodeSteim1

.. py:function:: encodeSteim1(samples: typing.Union[numpy.ndarray, list[int]], frames: int = 0, bias: numpy.int32 = 0, offset: int = 0) -> bytearray
   :canonical: simplemseed.steim1.encodeSteim1

   .. autodoc2-docstring:: simplemseed.steim1.encodeSteim1

.. py:function:: encodeSteim1FrameBlock(samples: typing.Union[numpy.ndarray, list[int]], frames: int = 0, bias: numpy.int32 = 0, offset: int = 0) -> simplemseed.steimframeblock.SteimFrameBlock
   :canonical: simplemseed.steim1.encodeSteim1FrameBlock

   .. autodoc2-docstring:: simplemseed.steim1.encodeSteim1FrameBlock

.. py:function:: extractSteim1Samples(dataBytes: bytearray, offset: int) -> list
   :canonical: simplemseed.steim1.extractSteim1Samples

   .. autodoc2-docstring:: simplemseed.steim1.extractSteim1Samples
