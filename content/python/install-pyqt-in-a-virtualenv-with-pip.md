Title: Install PyQt in a virtualenv with Pip
Date: 2013-05-30 15:48
Author: Sam Stoelinga
Category: Python
Tags: python, pyqt, pip
Slug: install-pyqt-in-a-virtualenv-with-pip

Noticed that pip install pyqt isn't working? At least at the time of
writing this blog it isn't..

This is the error that I got:  
IOError: [Errno 2] No such file or directory: setup.py

It seems they didn't package it well and it's using configure.py to
install. So here is the solution to install it by using pip to download
the files and configure and install manually.

**Solution** copied from: <http://stackoverflow.com/a/13967084/376445>

    :::bash
    workon myProject  
    pip install --no-install SIP  
    pip install --no-install PyQt  
    cd ~/.virtualenvs/myProject/build/SIP  
    python configure.py  
    make  
    make install  
    cd ~/.virtualenvs/myProject/build/PyQt  
    python configure.py  
    make  
    make install  
    cd && rm -rf ~/.virtualenvs/myProject/build # Optional.  

**Issues I encountered**:

- Missing development headers for qt: 

        :::bash
        ~/.virtualenvs/scrapy/build/PyQt# python configure.py --verbose  
        Determining the layout of your Qt installation...  
        /usr/bin/qmake -o qtdirs.mk qtdirs.pro  
        make -f qtdirs.mk 
        g++ -c -m64 -pipe -O2 -Wall -W -D_REENTRANT -DQT_NO_DEBUG
        -DQT_CORE_LIB -I/usr/share/qt4/mkspecs/linux-g++-64 -I.
        -I/usr/includ e/qt4/QtCore -I/usr/include/qt4 -I. -o qtdirs.o qtdirs.cpp  
        qtdirs.cpp:1:28: fatal error: QCoreApplication: No such file or directory compilation terminated.  
        make: *** [qtdirs.o] Error 1  
        Error: Failed to determine the layout of your Qt installation. Try again using  the --verbose flag to see more detail about the problem.  

**Soltution:** Install the development headers (Ubuntu 12.04)

    :::bash
    sudo apt-get install libqt4-dev  

