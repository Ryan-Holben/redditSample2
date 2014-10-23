# This script should be run separately from any other RedditDB things.
# It runs in a loop, adding information from the front page to the database.
# Leave it running to build the database in a continuous but lightway way.
# Every new post is tagged with a 'time_remaining' value, which will be the lifetime of its experiment

import os, sys, datetime, time, praw, pymongo
from praw.handlers import MultiprocessHandler

m = pymongo.MongoClient('mongodb://localhost:27017/')
db = m['reddit_sample']

def get_experiment_time():
  query = db.metadata.find_one({'experiment_time': {'$exists':True}})
  if query == None:
    print 'Error, no entry for experiment_time found in reddit_sample.metadata'
    exit()
  else:
    return query['experiment_time']

def load_subreddits(filename):
  f = open(filename, 'r')
  subreddits = f.read().lower().split()
  f.close()
  return subreddits
    
def utc_now():
  return (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()

def add_submission(post):
  if db.active_datasets.find_one({'id': post.id}) != None: return 0
  history = [ (utc_now(), post.score, post.num_comments) ]
  
  db.active_datasets.insert({   'finish_time': utc_now() + get_experiment_time(),
                                'id': post.id,
                                'author': str(post.author),
                                'created_utc': post.created_utc,
                                'title': post.title,
                                'subreddit': post.subreddit.display_name,
                                'domain': post.domain,
                                'selftext': post.selftext,
                                'gilded': post.gilded,
                                'history': history
                            })
  return 1

if __name__ == '__main__':
  print '\n'
  r = praw.Reddit('Reddit sampling experiment: gather_data.py v/0.1.', handler = MultiprocessHandler())
  experiment_start = time.time()
  
  while True:
    subreddits = load_subreddits('subreddits.txt')
    i = 0; j = 0
    for post in praw.helpers.submission_stream(r, subreddit = 'all', limit = None, verbosity = 0):
      if post.subreddit.display_name.lower() in subreddits:
        i += add_submission(post)
      j += 1
      print 'Iterated over:', j, '\tAdded:', i
      if (time.time()-experiment_start) > get_experiment_time()/2:
        print 'Time has elapsed.'
        exit()
