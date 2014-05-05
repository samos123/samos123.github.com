Title: Django Custom View Decorator with Arguments
Date: 2012-02-23 17:52
Author: Sam Stoelinga
Category: Python
Tags: django, python, coding, decorators
Slug: django-custom-view-decorator-with-arguments

To make my life easier I made a simple decorator which checks if the
parameters are present in the request.POST or request.GET and returns a
response if they are not.

It accepts a list of parameters in string format and will loop through
each parameter to check if they are present in the request.POST.

I noticed there weren't a lot of guides about how to write a decorator
for Django which takes arguments. I based my code on this tutorial, it's
a really great guide which helps you understand Python decorators at a
new level: [Amazing insight about Python
decorators](http://www.elfsternberg.com/2009/11/20/python-decorators-with-arguments-with-bonus-django-goodness/ "Amazing insight about Python decorators")

Here is the code I wrote for the decorator:  

    :::python
    def required_parameters(parameters=('email', 'api_key'), http_method='POST'):  
        """  
        Check if the required parameters are present in the request  
        @param parameters: The names of the parameters that should be supplied  
        """  
        def inner_decorator(fn):  
            def wrapped(request, *args, **kwargs):  
                # check if the user api_key matches  
                for parameter in parameters:  
                if parameter not in getattr(request, http_method):  
                    return json_response({'success': False, 'errors': 'Please use the Web API correctly and supply the parameter: '+parameter})  
                # Proceed like normally with the request  
                return fn(request, *args, **kwargs)  
            return wraps(fn)(wrapped)  
        return inner_decorator  
        [/python]

An example of using it in your view:  

    :::python
    @required_parameters(parameters=('email', 'username', 'password'))  
    def view_which_requires_email_username_and_password(request)  
        bla = 'bla'
        return HttpResponse(bla)  
