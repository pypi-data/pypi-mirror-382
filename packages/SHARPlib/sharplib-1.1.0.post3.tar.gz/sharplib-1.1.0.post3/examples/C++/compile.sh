export CPPFLAGS='--std=c++17 -g -O3 -Wall -ftree-vectorize -funroll-loops -march=native'
g++ $CPPFLAGS -I../../include/ -I../../external/fmt/include/ -c ../../src/SHARPlib/*.cpp
ar rcs SHARPlib_CXX.a *.o
g++ $CPPFLAGS -I../../include -o main main.cpp SHARPlib_CXX.a
