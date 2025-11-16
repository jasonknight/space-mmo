@echo off
set CommonCompilerFlags=-MT -nologo -Gm- -GR- -EHa- -Od -Oi -WX -W4 -I ..\ -wd4201 -wd4100 -wd4189 -DBUILD_INTERNAL=1 -DBUILD_SLOW=1 -DBUILD_WIN32=1 -FC -Z7 
set CommonLinkerFlags= -incremental:no -opt:ref user32.lib gdi32.lib winmm.lib xinput.lib ..\..\..\SDL3\lib\x86\SDL3.lib

pushd build
cl %CommonCompilerFlags% ..\examples\sdl.cpp /std:c++20 /EHsc /link %CommonLinkerFlags%
popd
