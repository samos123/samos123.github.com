Title: Move first word to end of line (Linux/awk)
Date: 2014-06-08 20:29
Author: Sam Stoelinga
Category: Linux
Slug: move-first-word-to-end-of-line-linux-awk


Move the first word of a line to the end of line on Linux using AWK.
We first store the first column(first word) in the variable t. Then
we set the first column to be empty. At last we add a new column
after the last column of the line which is stored in $NF.

    :::bash
    $ echo " move_to_end  should stay at the same place" | awk '{t=$1; $1=""; $(NF+1)=t}1
    should stay at the same place move_to_end

The idea was from a stackoverflow question which I can't find anymore.
