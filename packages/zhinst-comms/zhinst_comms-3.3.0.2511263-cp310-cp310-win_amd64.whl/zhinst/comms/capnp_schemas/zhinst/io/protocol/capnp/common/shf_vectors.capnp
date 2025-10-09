@0xb49d83187f644d94;

using Cxx = import "/capnp/c++.capnp";
$Cxx.allowCancellation;
$Cxx.namespace("zhinst_capnp");

using import "/zhinst/io/protocol/capnp/common/complex.capnp".Complex;

struct ShfDemodulatorVectorData @0x9b03e3e3e6006582 {
  properties :group {
    timestamp        @0  :UInt64;
    dt               @1  :UInt64;
    burstLength      @2  :UInt32;
    burstOffset      @3  :UInt32;
    triggerIndex     @4  :UInt32;
    triggerTimestamp @5  :UInt64;
    centerFreq       @6  :Float64;
    rfPath           @7  :Bool;
    oscillatorSource @8  :UInt16;
    harmonic         @9  :UInt16;
    triggerSource    @10 :UInt8;
    signalSource     @11 :UInt16;
    oscillatorFreq   @12 :Float64;
  }
  x @13 :List(Float64);
  y @14 :List(Float64);
}

struct ShfResultLoggerVectorData @0xbba061f579761ddd {
  properties :group {
    timestamp            @0  :UInt64;
    jobId                @1  :UInt32;
    repetitionId         @2  :UInt32;
    scaling              @3  :Float64;
    centerFrequency      @4  :Float64;
    dataSource           @5  :UInt32;
    numSamples           @6  :UInt32;
    numSpectrSamples     @7  :UInt32;
    numAverages          @8  :UInt32;
    numAcquired          @9  :UInt32;
    holdoffErrorsReslog  @10 :UInt16;
    holdoffErrorsReadout @11 :UInt16;
    holdoffErrorsSpectr  @12 :UInt16;
    firstSampleTimestamp @13 :UInt64;
  }
  vector :union {
    real    @14 :List(Float64);
    complex @15 :List(Complex);
  }
}

struct ShfScopeVectorData @0xa9b07f1f82a93bc9 {
  properties :group {
    timestamp         @0  :UInt64;
    timestampDiff     @1  :UInt32;
    flags             @2  :UInt32;
    scaling           @3  :Float64;
    centerFrequency   @4  :Float64;
    triggerTimestamp  @5  :UInt64;
    inputSelect       @6  :UInt32;
    averageCount      @7  :UInt32;
    numSegments       @8  :UInt32;
    numTotalSegments  @9  :UInt32;
    firstSegmentIndex @10 :UInt32;
    numMissedTriggers @11 :UInt32;
  }
  vector :union {
    real    @12 :List(Float64);
    complex @13 :List(Complex);
  }
}

struct ShfGeneratorWaveformVectorData @0xedcfe06e81c4f3d0 {
  complex @0 :List(Complex);
}

struct ShfPidVectorData @0xff6ee171549a2870 {
  properties :group {
    timestamp        @0  :UInt64;
    timestampDiff    @1  :UInt64;
    burstLength      @2  :UInt32;
    burstOffset      @3  :UInt32;
    triggerIndex     @4  :UInt32;
    triggerTimestamp @5  :UInt64;
    centerPoint      @6  :Float64;
    inputChannel     @7  :UInt8;
    input            @8  :UInt8;
    outputChannel    @9  :UInt8;
    output           @10 :UInt8;
    triggerSrc       @11 :UInt8;
    setPoint         @12 :Float64;
  }
  value @13 :List(Float64);
  error @14 :List(Float64);
}
