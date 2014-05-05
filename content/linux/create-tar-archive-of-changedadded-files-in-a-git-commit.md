Title: Create tar archive of changed/added files in a git commit
Date: 2013-05-02 02:12
Author: Sam Stoelinga
Category: Linux
Tags: git, linux, shell, bash
Slug: create-tar-archive-of-changedadded-files-in-a-git-commit

The following command first gets the changed and added files of a git
commit and then creates a tar archive of those changed files.

    :::bash
    git show {{COMMIT_ID}} --name-status | grep -Ew '^M|A' | awk '{ print $2 }' | xargs tar czf usb-passthrough.tar.gz
