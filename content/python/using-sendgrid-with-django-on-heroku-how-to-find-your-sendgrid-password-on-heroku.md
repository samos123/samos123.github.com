Title: Using Sendgrid with Django on Heroku (How to find your Sendgrid password on Heroku)
Date: 2012-04-11 09:43
Author: Sam Stoelinga
Category: Python
Slug: using-sendgrid-with-django-on-heroku-how-to-find-your-sendgrid-password-on-heroku

While setting up sentgrid I was searching for my password of sendgrid,
but coudn't find it. You can get it in the following way:

    :::bash
    heroku config --long

Which will show the parameters:  
SENDGRID\_PASSWORD, SENDGRID\_USERNAME

After you get your username don't forget to add it to django settings:  

    :::python2
    EMAIL\_HOST = 'smtp.sendgrid.net'  
    EMAIL\_HOST\_USER = 'app11111111@heroku.com'  
    EMAIL\_HOST\_PASSWORD = 'thepassyougotbefore'  
    EMAIL\_PORT = 587  
    EMAIL\_USE\_TLS = True  

Hope it helped somebody
