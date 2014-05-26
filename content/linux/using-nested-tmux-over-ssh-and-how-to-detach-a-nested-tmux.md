Title: Using nested tmux over ssh and how to detach a nested tmux
Date: 2013-08-15 02:08
Author: Sam Stoelinga
Category: Linux
Slug: using-nested-tmux-over-ssh-and-how-to-detach-a-nested-tmux

Today I logged in to my laptop at home from work which was already
running a tmux session, so thought yea just attach cool can continue
with what I was looking at at home. I forgot that the keys would be the
same ofcourse, and was unable to use the tmux session at my laptop at
home. Whenever I would type Ctrl + B + n etc it would do that on my work
desktop which was also running tmux. I was lolling oh damn how to get
out of that laptops tmux session.

Google to the rescue. Here is the solution:

If you want to access the tmux session inside the ssh session so in my
example on my laptop, you have to just use Ctrl + b + Ctrl + b

So if you want to detach the nested tmux session you have to execute the
following: (Ctrl + b) + (Ctrl + b) + d.

(Resource: [Tmux
Tips](http://fizbancyr.wordpress.com/2012/05/31/tmux-tips/))
