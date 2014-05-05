Title: Importing a SQL dump in postgres
Date: 2011-11-29 13:46
Author: Sam Stoelinga
Category: Linux
Slug: importing-a-sql-dump-in-postgres

I always keep forgetting how to import a SQL dump into postgres and
found it always hard to find the right documentation. So I thought lets
share it:

    :::bash
    psql -d dbname -U username -f dumpfile.sql

This should also work with files created by pgdump.
