@0xcc4004aa2313ccc4;

using Cxx = import "/capnp/c++.capnp";
# zhinst::capnp would be nicer than zhinst_capnp, but there's the chance of namespace
# collisions with the "capnp" namespace
$Cxx.namespace("zhinst_capnp");

using import "/zhinst/io/protocol/capnp/common/value.capnp".Value;

# Kwargs = Keyword arguments. Useful to mimic Python kwargs in RPC calls.
struct Kwargs @0x8f25ce07a664cee0 {
  entries @0 :List(Entry);
  struct Entry @0xa2644e6fd3dc2553 {
    key @0 :Text;
    value @1 :Value = (none = ());
  }
}
