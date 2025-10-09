@0xf7e8e31fdca4abd5;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("zhinst_capnp");

struct Result @0xbab0f33e1934323d (Type, Error) {
  union {
    ok @0 :Type;
    err @1 :Error;
  }
}
