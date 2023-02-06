Title: Python
Date: 2023-02-6 11:16
Author: Sam Stoelinga
Category: Python
Tags: python, uuid
Slug: python-create-uuid-from-integer

Code:
```python
import uuid
my_uuid = uuid.UUID(int=1)
print(my_uuid)
```

That should show the following string:
```
00000000-0000-0000-0000-000000000001
```

You can also convert back to integer by doing:
```python
my_uuid.int()
```


For my use case this was needed because my source database
has integer based IDs, however the destination database was using
UUID based IDs. So converting from integer to UUID was helpful to
ensure data can easily be deduplicated.

Review the Python UUID docs for more detailed explanation:
[Python official docs UUID](https://docs.python.org/3/library/uuid.html#uuid.UUID)


