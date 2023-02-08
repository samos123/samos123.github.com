Title: Python Create UUID from random string of words
Date: 2023-02-08 10:18
Author: Sam Stoelinga
Category: Python
Tags: python, uuid
Slug: python-create-uuid-from-random-string-of-words

Context: I'm loading data from one database (A) to another database (Weaviate).
Weaviate only supports UUID, however database A is using strings as the primary
identifier for some tables.

Problem: In order to not duplicate data I need to ensure that the string
identifier gets converted to an UUID in a deterministic way.

Solution: Use a hashing mechanism that produces a 128 bit integer, because
UUID also uses a 128 bit integer. The MD5 hashing algo is used as the solution.
The string is converted into an md5 hash and then the resulting 128 bit integer
is passed to Python `uuid.UUID` method.

Code:
```python
import uuid
import hashlib

def create_uuid_from_string(val: str):
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)

my_string = "a string used as unique identifier"
print(create_uuid_from_string(my_string))
```

That should show the following output:
```
b97c65e2-23a3-e77a-2225-b577e0bbbcd3
```

Note that result will be the same no matter how many times you
run it for the same string.
