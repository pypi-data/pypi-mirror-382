#!/bin/sh

echo "This script attempts to fetch and build DGGAL, DGG and its bindings and examples for C, C++, Python and Rust."
echo "Please make sure you have git installed to fetch the source code from the eC and DGGAL repositories."
echo "Please make sure you have zlib (dev package) installed, as well as GCC or Clang, and GNU Make."
echo "Please make sure you have GCC or Clang C++ support installed."
echo "Please make sure you have the Rust compiler (rustc) edition 2021+ installed."
echo "Please make sure you have cffi installed for Python (pip3 install cffi)."
echo ""
echo "Building in 'dgbuild' directory..."

mkdir dgbuild
cd dgbuild

echo "Fetching eC core development environment..."
git clone -b main --single-branch https://github.com/ecere/eC.git

echo "Fetching DGGAL..."
git clone -b eC-core --single-branch https://github.com/ecere/dggal.git

echo "Building eC development environment..."
cd eC
make -j4

echo "Building DGGAL..."
cd ../dggal/
make -j4

echo ""
echo "**************************************"
echo "************ DGGAL for eC ************"
echo "**************************************"
echo "Execution test for DGG tool:"
export LD_LIBRARY_PATH=$(pwd)/../eC/obj/linux/lib/:$(pwd)/obj/release.linux:$(pwd)/obj/linux/lib
obj/release.linux/dgg ISEA3H info A4-0-A
echo "Execution test for (static) DGG tool:"
obj/static.linux/dgg ISEA3H info A4-0-A

echo ""
echo "**************************************"
echo "************ DGGAL for C *************"
echo "**************************************"
echo "Building DGGAL for C..."
cd ../eC/bindings/c
make
cd ../../../dggal/bindings/c
make
echo "Building DGGAL sample C application..."
cd ../../bindings_examples/c
make
echo "Execution test for DGGAL sample C application:"
obj/release.linux/info ISEA3H A4-0-A
echo "Building DGGAL (static) sample C application..."
make -f Makefile.static
echo "Execution test for DGGAL (static) sample C application:"
obj/static.linux/info ISEA3H A4-0-A
cd ../..

echo ""
echo "**************************************"
echo "*** DGGAL for C (function wrappers) **"
echo "**************************************"
echo "Building DGGAL for C (function wrappers)..."
cd bindings/c_fn
make
echo "Building DGGAL sample C (function wrappers) application..."
cd ../../bindings_examples/c_fn
make
echo "Execution test for DGGAL sample C (function wrappers) application:"
obj/release.linux/info ISEA3H A4-0-A
cd ../..

echo ""
echo "**************************************"
echo "************ DGGAL for C++ ***********"
echo "**************************************"
echo "Building DGGAL for C++..."
cd ../eC/bindings/cpp
make
cd ../../../dggal/bindings/cpp
make
echo "Building DGGAL sample C++ application..."
cd ../../bindings_examples/cpp
make
echo "Execution test for DGGAL sample C++ application:"
obj/release.linux/info ISEA3H A4-0-A
echo "Building DGGAL (static) sample C++ application..."
make -f Makefile.static
echo "Execution test for DGGAL (static) sample C++ application:"
obj/static.linux/info ISEA3H A4-0-A
cd ../..

echo ""
echo "**************************************"
echo "*********** DGGAL for Rust ***********"
echo "**************************************"
echo "Building DGGAL for Rust..."
cd ../eC/bindings/rust
make
cd ../../../dggal/bindings/rust
make
echo "Building DGGAL sample Rust application..."
cd ../../bindings_examples/rust
make
echo "Execution test for DGGAL sample Rust application:"
obj/linux/info ISEA3H A4-0-A
cd ../..

echo ""
echo "**************************************"
echo "********** DGGAL for Python **********"
echo "**************************************"
echo "Building DGGAL for Python..."
cd ../eC/bindings/py
python3 build_ecrt.py
cd ../../../dggal/bindings/py
python3 build_dggal.py
echo "Execution test for DGGAL sample Python application:"
export PYTHONPATH=$(pwd):$(pwd)/../../../eC/bindings/py
cd ../../bindings_examples/py/
python3 info.py
cd ../..

echo ""
echo "All done! Thank you for trying out and using DGGAL."
