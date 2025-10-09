def _cmake_to_bool(s):
    return s.upper() not in ['', '0','FALSE','OFF','N','NO','IGNORE','NOTFOUND']

is_python_package    = _cmake_to_bool("TRUE")

BUILD_STUB_FILES     = _cmake_to_bool("OFF")
BUILD_UMFPACK        = _cmake_to_bool("")
ENABLE_UNIT_TESTS    = _cmake_to_bool("OFF")
INSTALL_DEPENDENCIES = _cmake_to_bool("OFF")
USE_CCACHE           = _cmake_to_bool("ON")
USE_HYPRE            = _cmake_to_bool("OFF")
USE_LAPACK           = _cmake_to_bool("ON")
USE_MKL              = _cmake_to_bool("ON")
USE_MUMPS            = _cmake_to_bool("OFF")
USE_PARDISO          = _cmake_to_bool("OFF")
USE_UMFPACK          = _cmake_to_bool("OFF")

NETGEN_DIR = "C:/gitlabci/tools/builds/3zsqG5ns/0/ngsolve/venv_ngs/Lib/site-packages"

NGSOLVE_COMPILE_DEFINITIONS         = "HAVE_NETGEN_SOURCES;USE_TIMEOFDAY;TCL;LAPACK;USE_PARDISO;NGS_PYTHON"
NGSOLVE_COMPILE_DEFINITIONS_PRIVATE = "USE_MKL"
NGSOLVE_COMPILE_INCLUDE_DIRS        = ""
NGSOLVE_COMPILE_OPTIONS             = "/std:c++17;/bigobj;/wd4068;-DMAX_SYS_DIM=3"

NGSOLVE_INSTALL_DIR_PYTHON   = "."
NGSOLVE_INSTALL_DIR_BIN      = "netgen"
NGSOLVE_INSTALL_DIR_LIB      = "netgen/lib"
NGSOLVE_INSTALL_DIR_INCLUDE  = "netgen/include"
NGSOLVE_INSTALL_DIR_CMAKE    = "ngsolve/cmake"
NGSOLVE_INSTALL_DIR_RES      = "share"

NGSOLVE_VERSION = "6.2.2506-74-gd430159c1"
NGSOLVE_VERSION_GIT = "v6.2.2506-74-gd430159c1"
NGSOLVE_VERSION_PYTHON = "6.2.2506.post74.dev0"

NGSOLVE_VERSION_MAJOR = "6"
NGSOLVE_VERSION_MINOR = "2"
NGSOLVE_VERSION_TWEAK = "74"
NGSOLVE_VERSION_PATCH = "2506"
NGSOLVE_VERSION_HASH = "gd430159c1"

CMAKE_CXX_COMPILER           = "C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/cl.exe"
CMAKE_CUDA_COMPILER          = ""
CMAKE_C_COMPILER             = "C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/cl.exe"
CMAKE_LINKER                 = "C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/link.exe"
CMAKE_INSTALL_PREFIX         = "C:/gitlabci/tools/builds/3zsqG5ns/0/ngsolve/ngsolve/_skbuild/win-amd64-3.13/cmake-install"
CMAKE_CXX_COMPILER_LAUNCHER  = ""

version = NGSOLVE_VERSION_GIT

MKL_LINK = "sdl"

def get_cmake_dir():
    import os.path as p
    d_python = p.dirname(p.dirname(p.dirname(__file__)))
    py_to_cmake = p.relpath(
            NGSOLVE_INSTALL_DIR_CMAKE,
            NGSOLVE_INSTALL_DIR_PYTHON
            )
    return p.normpath(p.join(d_python,py_to_cmake))
