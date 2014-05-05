Title: How to install Setuptools to a specific python version
Date: 2011-07-18 19:34
Author: Sam Stoelinga
Category: Python
Tags: python, ubuntu, linux
Slug: how-to-install-setuptools-to-a-specific-python-version

To install easy\_install for a specific python version. I just installed
from source and used the python version you want to install setuptools
too. I used the following steps in Ubuntu 11.04 with Python 2.5 and
Python 2.7 installed. The following commands will install setuptools to
python 2.5  

    :::bash
    wget
    http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz#md5=7df2a529a074f613b509fb44feefe74e  
    tar -zxvf setuptools-0.6c11.tar.gz cd setuptools-0.6c11/  
    sudo python2.5 setup.py install  

The following command installs the pil module to 2.5:   
`sudo easy_install-2.5 pil`

This command installs the pil module to 2.7:   
`sudo easy\_install-2.7 pil`
