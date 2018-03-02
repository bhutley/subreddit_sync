# subreddit_sync.py #

This tool is for syncing the submissions and comments from a subreddit to a SQLite database.
The database will be created if it does not exist. There are two tables - 'submission' and 'comment'.
You can specify a time-limit for what submissions should be retrieved - by default is 'day'. 'all' only seems to get the last 100 submissions.
You can get an individual submission by id.

Re-running this tool will add new submissions and add new comments to existing submissions (if there are any).

