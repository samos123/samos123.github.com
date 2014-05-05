Title: Simple function to return json in Django
Date: 2012-02-22 15:53
Author: Sam Stoelinga
Category: Python
Tags: python, django, json
Slug: simple-function-to-return-json-in-django

Just a small code snippet I use when I need to return json, comments are
welcomed.

    :::python
    from django.http import HttpResponse  
    from django.utils import simplejson as json

    def json_response(dict_to_convert_to_json):  
        return HttpResponse(json.dumps(dict_to_convert_to_json),
                            mimetype="application/json")  

To use it in your view you just do it this way:  

    :::python
    def login(request):  
        return json_response({'success' : True, 'user' : {'name': 'Sam',
                                                          'speciality': 'Django/Python'}})

You could also create a decorator to do this but I think using a simple function
is more straight forward.
