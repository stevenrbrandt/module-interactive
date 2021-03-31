FROM fedora

RUN dnf install -y vim findutils gcc gcc-c++ make git svn curl cmake python3 \
                   boost-devel gperftools-devel hwloc-devel libatomic vim gdb file \
                   python3-pybind11 python3-devel python3-numpy python3-matplotlib

ENV BUILD_PROCS 20

#COPY clang-build.sh /usr/local/bin/
#RUN bash /usr/local/bin/clang-build.sh
RUN dnf install -y clang libcxx-devel

COPY cxx17_shared_ptr_array.cpp /usr/local/include
COPY hpx-build.sh /usr/local/bin/
RUN bash /usr/local/bin/hpx-build.sh

RUN python3 -m ensurepip
RUN python3 -m pip install jupyter termcolor
RUN mkdir -p /usr/local/python
WORKDIR /usr/local/python
COPY runcode.py .
WORKDIR /usr/local/src
COPY clangw.cpp .
COPY clangw.cppm .
COPY clangwpy11.cpp .
COPY Seg.hpp .
COPY runtime_support.hpp /usr/local/include/hpx/runtime/components/server/

RUN useradd -m jovyan

COPY demo.ipynb /home/jovyan/
RUN chown jovyan /home/jovyan/demo.ipynb

USER jovyan
WORKDIR /home/jovyan
ENV PYTHONPATH /usr/local/python

CMD jupyter notebook --ip 0.0.0.0 --port $PORT
