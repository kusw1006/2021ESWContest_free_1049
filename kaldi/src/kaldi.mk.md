# Kaldi.mk

> Path: /opt/kaldi/src



> 설명:
>
> 1. ```/opt/kaldi/tools/extras/install_mkl.sh 실행```
>
> 2. /opt/kaldi/src에서
>
>    ```./configure --shared --mkl-root="/opt/intel/mkl" --mkl-libdir="/opt/intel/mkl/lib/intel64"```
>
> 3. /opt/kaldi/src에서 
>
>    ```sudo make depend && sudo make -j 16``` 이전에 아래의 코드 복붙
>
> 4. 이후 /opt에서 ```sudo sh kusw_start.sh 실행``` 및 ``` sudo python /tmp/client.py .... 입력```

```makefile
# This file was generated using the following command:
# ./configure --shared --mkl-root=/opt/intel/mkl --mkl-libdir=/opt/intel/mkl/lib/intel64

CONFIGURE_VERSION := 14

# Toolchain configuration

CXX = g++
AR = ar
AS = as
RANLIB = ranlib

# Target achitecture
ARCH = x86_64

# Base configuration

KALDI_FLAVOR := dynamic
KALDILIBDIR := /opt/kaldi/src/lib
DEBUG_LEVEL = 1
DOUBLE_PRECISION = 0
OPENFSTINC = /opt/kaldi/tools/openfst-1.7.2/include
OPENFSTLIBS = /opt/kaldi/tools/openfst-1.7.2/lib/libfst.so
OPENFSTLDFLAGS = -Wl,-rpath=/opt/kaldi/tools/openfst-1.7.2/lib

CUBROOT = /opt/kaldi/tools/cub-1.8.0
WITH_CUDADECODER = true

MKL_CXXFLAGS = -I/opt/intel/mkl/include
MKL_LDLIBS = -L/opt/intel/mkl/lib/intel64_lin -Wl,-rpath=/opt/intel/mkl/lib/intel64_lin -l:libmkl_rt.so -l:libmkl_sequential.so -ldl -lpthread -lm

# MKL specific Linux configuration

# The linking flags for MKL will be very different depending on the OS,
# architecture, compiler, etc. used. In case configure did not cut it, use
# http://software.intel.com/en-us/articles/intel-mkl-link-line-advisor/

ifndef DEBUG_LEVEL
$(error DEBUG_LEVEL not defined.)
endif
ifndef DOUBLE_PRECISION
$(error DOUBLE_PRECISION not defined.)
endif
ifndef OPENFSTINC
$(error OPENFSTINC not defined.)
endif
ifndef OPENFSTLIBS
$(error OPENFSTLIBS not defined.)
endif

CXXFLAGS = -std=c++14 -I.. -isystem $(OPENFSTINC) -O1 \
           -Wall -Wno-sign-compare -Wno-unused-local-typedefs \
           -Wno-deprecated-declarations -Winit-self \
           -DKALDI_DOUBLEPRECISION=$(DOUBLE_PRECISION) \
           -DHAVE_EXECINFO_H=1 -DHAVE_CXXABI_H -DHAVE_MKL $(MKL_CXXFLAGS) \
           -m64 -msse -msse2 -pthread -g

ifeq ($(KALDI_FLAVOR), dynamic)
CXXFLAGS += -fPIC
endif

ifeq ($(DEBUG_LEVEL), 0)
CXXFLAGS += -DNDEBUG
endif
ifeq ($(DEBUG_LEVEL), 2)
CXXFLAGS += -O0 -DKALDI_PARANOID
endif

# Compiler specific flags
COMPILER = $(shell $(CXX) -v 2>&1)
ifeq ($(findstring clang,$(COMPILER)),clang)
# Suppress annoying clang warnings that are perfectly valid per spec.
CXXFLAGS += -Wno-mismatched-tags
endif

# As late as possible to allow the user to do what they want.
CXXFLAGS += $(EXTRA_CXXFLAGS)

LDFLAGS = $(OPENFSTLDFLAGS) -rdynamic $(EXTRA_LDFLAGS)
LDLIBS =  $(EXTRA_LDLIBS) $(OPENFSTLIBS) $(MKL_LDLIBS) -lm -lpthread -ldl

# CUDA configuration

CUDA = true
CUDATKDIR = /usr/local/cuda
CUDA_ARCH = -gencode arch=compute_30,code=sm_30 -gencode arch=compute_35,code=sm_35 -gencode arch=compute_50,code=sm_50 -gencode arch=compute_52,code=sm_52 -gencode arch=compute_60,code=sm_60 -gencode arch=compute_61,code=sm_61 -gencode arch=compute_70,code=sm_70 -gencode arch=compute_75,code=sm_75
HOST_ARCH = x86_64

ifndef DOUBLE_PRECISION
$(error DOUBLE_PRECISION not defined.)
endif
ifndef CUDATKDIR
$(error CUDATKDIR not defined.)
endif

CXXFLAGS += -DHAVE_CUDA -I$(CUDATKDIR)/include -fPIC -pthread -isystem $(OPENFSTINC)

CUDA_INCLUDE= -I$(CUDATKDIR)/include -I$(CUBROOT) -I.. -isystem $(OPENFSTINC)
CUDA_FLAGS = --compiler-options -fPIC --machine 64 -DHAVE_CUDA \
             -ccbin $(CXX) -DKALDI_DOUBLEPRECISION=$(DOUBLE_PRECISION) \
             -std=c++14 -DCUDA_API_PER_THREAD_DEFAULT_STREAM -lineinfo \
             --verbose -Wno-deprecated-gpu-targets

CUDA_LDFLAGS += -L$(CUDATKDIR)/lib64/stubs -L$(CUDATKDIR)/lib64 -Wl,-rpath,$(CUDATKDIR)/lib64
CUDA_LDFLAGS += -L$(CUDATKDIR)/lib/stubs -L$(CUDATKDIR)/lib -Wl,-rpath,$(CUDATKDIR)/lib

CUDA_LDLIBS += -lcuda -lcublas -lcusparse -lcusolver -lcudart -lcurand -lcufft -lnvToolsExt
CUDA_LDLIBS += -lcusolver

# Environment configuration


```

