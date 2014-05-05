Title: Only use worker when required on heroku with Django/Python
Date: 2012-04-13 09:42
Author: Sam Stoelinga
Category: Python
Tags: coding, python, django, heroku
Slug: only-use-worker-when-required-on-heroku-with-djangopython

For a mobile project I required a background worker which sents an email
with 300 generated QR codes zipped together as attachment. This costs
quite some time so we need a background worker to execute this task.

I wanted to achieve the following result:

-   When the user wants to generate qr codes, Start the celery worker
    process with scale(1)
-   Delay the celery task to be executed by the celeryworker
-   After our task is finished, stop the celeryworker with scale(0)

Why I want this? Well workers costs quite some money if they are running
constantly, which is in our case maybe only 1 hour a month. Saving us
about \$30 / month.

For more information about how to run a worker check the [Official
Heroku Django
documentation](https://devcenter.heroku.com/articles/django#running_a_worker),
which shows you how to setup Django with celery. Here you can find how
to create the task itself in celery: [Django-celery
tutorial](http://ask.github.com/django-celery/getting-started/index.html).

To talk with the Heroku REST API we are using
[Heroku.py](https://github.com/heroku/heroku.py). This API let's us
scale and stop / start proccesses with Python. The official
documentation tells to do it this way:

    :::python
    import heroku  
    cloud = heroku.from_key(settings.HEROKU_APIKEY)  
    app.processes['celeryd'].scale(1)  
    # now execute our celerytask  
    generate_qr_codes.delay(product_id=product.id)  

The only problem is that this line actually does not work:

    :::python
    app.processes['celeryd'].scale(1)

It will give an KeyError exception, because the celeryd is not running
which is kind of a bug, thats why I want to scale it to 1 in the first
place...

So I got stuck on that problem, but after checking out the Heroku
Python library I decided to use their internal API as they have an easy way of
calling Heroku HTTP resources. It's a quick work around to do what I
wanted:  

    :::python
    cloud._http_resource(method='POST',
                        resource=('apps', 'heroku_processname', 'ps', 'scale'),  
    data={'type': 'celeryd', 'qty': 0})
    # qty 0 is scale to 0 processes, if you want 1 process running change to qty 1  

I have created an issue in the github repo about not being able to scale
a non running process: <https://github.com/heroku/heroku.py/issues/10>

This is how our celery task looks like:  

    :::python
    import logging  
    from celery.decorators import task

    @task()  
    def generate_qrs(product_id):  
        try:  
            y = x + product_id  
            # this is where your code will be that gets executed in the background  
        except Exception, e:  
            logging.exception('Exception occured in the celery task to generate QR codes')  
        if settings.DEBUG == False:
            import heroku
            cloud = heroku.from_key(settings.HEROKU_APIKEY)  
            app = cloud.apps['appname']  
            cloud._http_resource(method='POST', resource=('apps', 'heroku_processname', 'ps', 'scale'),
                                 data={'type': 'celeryd', 'qty': 0})
            # the above line will stop the celeryd worker, so we dont have to pay
            # for the woker only when it's actually executing tasks  
