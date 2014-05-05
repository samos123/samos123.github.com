Title: Ubuntu 11.10 error while loading shared libraries: libssl.so.0.9.8: cannot open shared object file: No such file or directory
Date: 2011-10-29 06:15
Author: Sam Stoelinga
Category: Linux
Slug: ubuntu-11-10-error-while-loading-shared-libraries-libssl-so-0-9-8-cannot-open-shared-object-file-no-such-file-or-directory

A quick solution is to install the libssl 0.9.8 package with the
**Following command**:  
`sudo apt-get install libssl0.9.8`

Thanks to Rob who commented below and provided an answer on
[Stackoverflow](http://stackoverflow.com/questions/7937225/django-runserver-error-while-loading-shared-libraries-libssl-so-0-9-8-cannot-o)

I just upgraded from ubuntu 11.04 to 11.10 with a fresh install, by
keeping my old home folder so not loosing my personal data, but only
formatting the whole system partition. After reinstalling my most
important development software I still couldn't run django's server. I
kept getting the followering error:  
error while loading shared libraries: libssl.so.0.9.8:
cannot open shared object file: No such file or directory  

You will also get this error:  
python: error while loading shared libraries:
libcrypto.so.0.9.8: cannot open shared object file: No such file or
directory

It seems this problem was because the virtualenv was still using the
previous python libraries, which linked to a no longer there ssl
package, what I did was create a new virtualenv and problem was solved.
Anybody know a better way? Is there a way to update virtualenv to a new
python version?

Update: Seems it's just the upgrade process is too buggy normally.
I really enjoy Archlinux and recommend it to anybody who hates these
kind of issues.
