#!/usr/bin/env python
#
# subreddit_sync.py
#
# Author: Brett Hutley <brett@hutley.net>
#
# This tool is for syncing the submissions and comments from a subreddit to a SQLite database
# The database will be created if it does not exist.
# You can specify a time-limit for what submissions should be retrieved - by default is 'day'. 'all' only seems to get the last 100 submissions
# You can get an individual submission by id.
import os
import praw
from ConfigParser import SafeConfigParser
from optparse import OptionParser
import sqlite3

valid_time_options = ['all', 'year', 'month', 'week', 'day', 'hour', ]

optp = OptionParser()
optp.add_option("-c", "--config", dest="config_file", metavar="FILE",
                default= os.path.join(os.path.expanduser("~"), ".reddit.cfg"),
                help="Reddit configuration file")
optp.add_option("-n", "--name", dest="name", 
                default="brettbot",
                help="Bot Name")
optp.add_option("-l", "--limit", dest="limit", type="string",
                default="day",
                help="Submission time limit (%s)" % (",".join(valid_time_options), ))
optp.add_option("-s", "--subreddit", dest="subreddit", type="string",
                default=None,
                help="Subreddit name")
optp.add_option("-d", "--database", dest="database", type="string",
                default="reddit.db",
                help="Database name")
optp.add_option("-i", "--sb_id", dest="subid", type="string",
                default=None,
                help="Get a particular submission")

opts, args = optp.parse_args()

if not os.path.exists(opts.config_file):
    print("config file '%s' doesn't exist" % opts.config_file)
    exit(1)

if not opts.subreddit or len(opts.subreddit) == 0:
    print("A subreddit must be specified")
    exit(1)

if opts.limit not in valid_time_options:
    print("Invalid time option. Should be in %s" % ('/'.join(valid_time_options), ))
    exit(1)

config_parser = SafeConfigParser()
config_parser.read(opts.config_file)

client_id = config_parser.get(opts.name, 'client_id')
client_secret = config_parser.get(opts.name, 'client_secret')

create_db = False
if not os.path.isfile(opts.database):
    create_db = True
    
conn = sqlite3.connect(opts.database)
if create_db:
    c = conn.cursor()
    c.execute('''CREATE TABLE submission(sb_id TEXT NOT NULL PRIMARY KEY, sr_name TEXT NOT NULL, author_name TEXT NOT NULL, created_utc REAL NOT NULL, title TEXT NOT NULL, permalink TEXT NOT NULL, url TEXT NOT NULL, selftext TEXT NOT NULL, num_comments INTEGER NOT NULL)''')
    c.execute('''CREATE INDEX x_submission_sr_name ON submission(sr_name)''')
    c.execute('''CREATE TABLE comment(cm_id TEXT NOT NULL PRIMARY KEY, sb_id TEXT NOT NULL, parent_id TEXT, author_name TEXT NOT NULL, created_utc REAL NOT NULL, body TEXT NOT NULL, permalink TEXT NOT NULL)''')
    c.execute('''CREATE INDEX x_comment_sb_id ON comment(sb_id)''')
    conn.commit()

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent='test script')
sr = reddit.subreddit(opts.subreddit)
sr_name = str(sr.name)

save_sub_id = opts.subid

c = conn.cursor()
all_sub_ids = {}
for row in c.execute('''SELECT sb_id, num_comments from submission WHERE sr_name=?;''', (sr_name, )):
    all_sub_ids[row[0]] = int(row[1])

def save_submission(post):
    sub_id = post.id
    num_comments_stored = 0
    if sub_id not in all_sub_ids:
        title = post.title
        author_name = ''
        if post.author is not None:
            author_name = post.author.name
        permalink = post.permalink
        url = post.url
        created_utc = float(post.created_utc)
        selftext = post.selftext
        num_comments = int(post.num_comments)
        c.execute('''INSERT INTO submission(sb_id, sr_name, author_name, created_utc, title, permalink, url, selftext, num_comments) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''', (sub_id, sr_name, author_name, created_utc, title, permalink, url, selftext, num_comments ))
    else:
        num_comments_stored = all_sub_ids[sub_id]
        
    num_comments = int(post.num_comments)
    if num_comments_stored != num_comments:
        c.execute('''UPDATE submission SET num_comments=? WHERE sb_id=?''', (num_comments, sub_id))
        all_comm_ids = set()
        for row in c.execute("SELECT cm_id FROM comment WHERE sb_id=?", ( sub_id, )):
            all_comm_ids.add(row[0])
        post.comments.replace_more(limit=None)
        for comment in post.comments.list():
            comm_id = comment.id
            author_name = ''
            if comment.author is not None:
                author_name = comment.author.name
            parent_id = comment.parent_id
            permalink = comment.permalink
            created_utc = float(comment.created_utc)
            body = comment.body

            if comm_id not in all_comm_ids:
                c.execute('''INSERT INTO comment(cm_id, sb_id, parent_id, author_name, created_utc, body, permalink) VALUES (?, ?, ?, ?, ?, ?, ?)''', (
                    comm_id, sub_id, parent_id, author_name, created_utc, body, permalink))

if save_sub_id is None or len(save_sub_id) == 0:
    submissions = sr.top(opts.limit)
    for post in submissions:
        save_submission(post)
else:
    post = reddit.submission(id=save_sub_id)
    save_submission(post)
    
conn.commit()

