Title: Trying to install scrapy with pip lxml error: command 'gcc' failed with exit status 1
Date: 2011-11-01 14:31
Author: Sam Stoelinga
Category: Python
Tags: python, linux, ubuntu
Slug: trying-to-install-scrapy-with-pip-lxml-error-command-gcc-failed-with-exit-status-1

Just tried to install scrapy with pip / easy\_install, but when it comes
to installing lxml it will give the following error:

gcc -pthread -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2
-Wall -Wstrict-prototypes -fPIC -I/usr/include/python2.7 -c
src/lxml/lxml.etree.c -o
build/temp.linux-x86\_64-2.7/src/lxml/lxml.etree.o -w

In file included from src/lxml/lxml.etree.c:239:0:
src/lxml/etree\_defs.h:9:31: fatal error: libxml/xmlversion.h: No such
file or directory
compilation terminated.

error: command 'gcc' failed with exit status 1  

**The solution**  
Install Python development package:

    :::bash
    sudo apt-get install python-dev

Install the development packages of libxml and libst  

    :::bash
    sudo apt-get install libxml2-dev  
    sudo apt-get install libxslt1-dev[/sourcecode]
