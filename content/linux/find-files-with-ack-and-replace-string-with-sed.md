Title: Find files with ack and replace string with sed
Date: 2023-02-10 12:10
Author: Sam Stoelinga
Category: Linux
Slug: find-files-with-ack-and-replace-string-with-sed

ack is a nice to tool to search in files in your current directory and subdirectores, but
ack won't do search and replace. Luckily, we can easily combine ack and sed using xargs.


```shell
ack -l "app.kubernetes.io/name: myapp" | xargs sed -i 's|app.kubernetes.io/name: myapp|app.kubernetes.io/name: "{{ .Release.name }}"|g'
```

This example searches for the string `app.kubernetes.io/name: myapp` through all files
and subdirs from current directory and tell ack to only output file names with the `-l` option.
Then we use xargs to append the filename to the end of the sed command.

