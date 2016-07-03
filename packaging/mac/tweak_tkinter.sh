#!/usr/bin/env bash

# take from env
# LOCAL_FRAMEWORKS=$HOME/thonny_template_build/Thonny.app/Contents/Frameworks
# PREFIX=$HOME/thonny_template_build
# mkdir -p $LOCAL_FRAMEWORKS

# Official tkinter is compiled against Tk 8.5, I want 8.6 #################################
# Let's compile one against 8.6
PYTHON_VERSION=3.5.2
RELEASE_NAME=Python-${PYTHON_VERSION}

INITIAL_DIR=$(pwd)
TEMP_DIR=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/temp_build_dir
rm -rf $TEMP_DIR/*

cd $TEMP_DIR
curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/$RELEASE_NAME.tgz
tar xf $RELEASE_NAME.tgz
cd $RELEASE_NAME

TCLI=/Library/Frameworks/Tcl.framework/Versions/8.6/Headers
TCLL=/Library/Frameworks/Tcl.framework/Versions/8.6
TKI=/Library/Frameworks/Tk.framework/Versions/8.6/Headers
TKL=/Library/Frameworks/Tk.framework/Versions/8.6

# https://github.com/python/cpython/tree/master/Mac
export MACOSX_DEPLOYMENT_TARGET=10.6
export CFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6 -I$PREFIX/include"
export LDFLAGS="-arch i386 -arch x86_64 -mmacosx-version-min=10.6 -L$PREFIX/lib"
export CXXFLAGS="$CFLAGS"
export ARCHFLAGS="-arch i386 -arch x86_64"

./configure --prefix=$PREFIX --enable-universalsdk --with-universal-archs=intel \
	--with-tcltk-includes="-I$TCLI -I$TKI " \
	--with-tcltk-libs="-I$TCLL -I$TKL -ltk8.6 -ltcl8.6" 	

make
make altinstall # TODO: copy from build dir??
cd $INITIAL_DIR


# Copy to framework template ###############################################################
TKINTER_FILENAME=_tkinter.cpython-35m-darwin.so
LOCAL_TKINTER=$LOCAL_FRAMEWORKS/Python.framework/Versions/3.5/lib/python3.5/lib-dynload/$TKINTER_FILENAME
TKINTER86=$PREFIX/lib/python3.5/lib-dynload/$TKINTER_FILENAME
cp -f $TKINTER86 $LOCAL_TKINTER

chmod u+w $LOCAL_TKINTER

# Update links ##############################################################################
install_name_tool -change \
    /Library/Frameworks/Tcl.framework/Versions/8.6/Tcl \
	@rpath/Tcl.framework/Versions/8.6/Tcl \
    $LOCAL_TKINTER 

install_name_tool -change \
    /Library/Frameworks/Tk.framework/Versions/8.6/Tk \
	@rpath/Tk.framework/Versions/8.6/Tk \
    $LOCAL_TKINTER 
