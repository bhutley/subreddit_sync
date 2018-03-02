# subreddit_sync.py #

This tool is for syncing the submissions and comments from a subreddit to a SQLite database.
The database will be created if it does not exist. 

There are two tables - 'submission' and 'comment'.

When running this script, you need to specify the particular subreddit you want to sync using the '-s' parameter.

You can specify a time-limit for what submissions should be retrieved by using the '-l' parameter. The default limit is 'day'. 'all' only seems to get the last 100 submissions.

You can get an individual submission by id using the '-i' parameter.

Re-running this tool will add new submissions and add new comments to existing submissions (if there are any).

This script depends on a config file (by default ~/.reddit.cfg) that contains your Reddit authentication secrets.
[This page has more details on getting these](https://praw.readthedocs.io/en/latest/getting_started/authentication.html)

The .reddit.cfg file looks like this:

    [botname]
    client_id=XXXXXXXXX
    client_secret=YYYYYYYYY

The 'botname' can be specified on the command-line. By default it is 'brettbot'

