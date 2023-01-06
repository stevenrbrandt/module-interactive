set -e
cd /
git clone --depth 1 -b 1.8.1 https://github.com/STEllAR-GROUP/hpx.git
cp /usr/local/include/cxx17_shared_ptr_array.cpp /hpx/cmake/tests/cxx17_shared_ptr_array.cpp
rm -fr /hpx/build
mkdir -p /hpx/build
cd /hpx/build
cmake \
    -DHPX_WITH_EXAMPLES=OFF \
    -DHPX_WITH_MORE_THAN_64_THREADS=ON \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DHPX_WITH_CXX_STANDARD=20 \
    -DCMAKE_CXX_FLAGS=-stdlib=libc++ \
    -DHPX_WITH_FETCH_ASIO=ON \
    ..
make -j${BUILD_PROCS} install
rm -fr /hpx/build
