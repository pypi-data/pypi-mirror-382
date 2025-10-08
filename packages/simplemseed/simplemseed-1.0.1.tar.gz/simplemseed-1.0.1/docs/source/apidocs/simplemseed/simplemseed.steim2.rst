:py:mod:`simplemseed.steim2`
============================

.. py:module:: simplemseed.steim2

.. autodoc2-docstring:: simplemseed.steim2
   :allowtitles:

Module Contents
---------------

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`bitsForPack <simplemseed.steim2.bitsForPack>`
     - .. autodoc2-docstring:: simplemseed.steim2.bitsForPack
          :summary:
   * - :py:obj:`decodeSteim2 <simplemseed.steim2.decodeSteim2>`
     - .. autodoc2-docstring:: simplemseed.steim2.decodeSteim2
          :summary:
   * - :py:obj:`encodeSteim2 <simplemseed.steim2.encodeSteim2>`
     - .. autodoc2-docstring:: simplemseed.steim2.encodeSteim2
          :summary:
   * - :py:obj:`encodeSteim2FrameBlock <simplemseed.steim2.encodeSteim2FrameBlock>`
     - .. autodoc2-docstring:: simplemseed.steim2.encodeSteim2FrameBlock
          :summary:
   * - :py:obj:`extractDnibValues <simplemseed.steim2.extractDnibValues>`
     - .. autodoc2-docstring:: simplemseed.steim2.extractDnibValues
          :summary:
   * - :py:obj:`extractSteim2Samples <simplemseed.steim2.extractSteim2Samples>`
     - .. autodoc2-docstring:: simplemseed.steim2.extractSteim2Samples
          :summary:
   * - :py:obj:`minBitsNeeded <simplemseed.steim2.minBitsNeeded>`
     - .. autodoc2-docstring:: simplemseed.steim2.minBitsNeeded
          :summary:
   * - :py:obj:`steimPackWord <simplemseed.steim2.steimPackWord>`
     - .. autodoc2-docstring:: simplemseed.steim2.steimPackWord
          :summary:

API
~~~

.. py:function:: bitsForPack(minbits: list[int], points_remaining: int)
   :canonical: simplemseed.steim2.bitsForPack

   .. autodoc2-docstring:: simplemseed.steim2.bitsForPack

.. py:function:: decodeSteim2(dataBytes: bytearray, numSamples: int, bias: int = 0)
   :canonical: simplemseed.steim2.decodeSteim2

   .. autodoc2-docstring:: simplemseed.steim2.decodeSteim2

.. py:function:: encodeSteim2(samples: typing.Union[numpy.ndarray, list[int]], frames: int = 0, bias: numpy.int32 = 0)
   :canonical: simplemseed.steim2.encodeSteim2

   .. autodoc2-docstring:: simplemseed.steim2.encodeSteim2

.. py:function:: encodeSteim2FrameBlock(samples: typing.Union[numpy.ndarray, list[int]], frames: int = 0, bias: numpy.int32 = 0) -> simplemseed.steimframeblock.SteimFrameBlock
   :canonical: simplemseed.steim2.encodeSteim2FrameBlock

   .. autodoc2-docstring:: simplemseed.steim2.encodeSteim2FrameBlock

.. py:function:: extractDnibValues(tempInt, headerSize, diffCount, bitSize)
   :canonical: simplemseed.steim2.extractDnibValues

   .. autodoc2-docstring:: simplemseed.steim2.extractDnibValues

.. py:function:: extractSteim2Samples(dataBytes: bytearray, offset: int, littleEndian: bool) -> numpy.ndarray
   :canonical: simplemseed.steim2.extractSteim2Samples

   .. autodoc2-docstring:: simplemseed.steim2.extractSteim2Samples

.. py:function:: minBitsNeeded(diff: int)
   :canonical: simplemseed.steim2.minBitsNeeded

   .. autodoc2-docstring:: simplemseed.steim2.minBitsNeeded

.. py:function:: steimPackWord(diff: list[int], nbits: int, ndiff: int, bitmask: numpy.int32, submask: numpy.int32) -> numpy.int32
   :canonical: simplemseed.steim2.steimPackWord

   .. autodoc2-docstring:: simplemseed.steim2.steimPackWord
