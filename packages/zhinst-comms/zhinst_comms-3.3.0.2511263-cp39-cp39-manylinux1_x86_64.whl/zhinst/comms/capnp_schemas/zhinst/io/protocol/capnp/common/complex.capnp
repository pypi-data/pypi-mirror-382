@0xd1631416fe8e50e9;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("zhinst_capnp");

struct Complex @0xaaf1afaf97b4b157 {
  real @0 :Float64;
  imag @1 :Float64;
}
