# This script should be run separately from any other RedditDB things.
# It runs in a loop, polling the Mongo database, updating existing posts every 2 minutes until some hard limit is reached
# New posts are added in a separate thread by gather_data.py
# Once a post is finished, it gets moved from db.active_datasets to db.datasets
# Ever

import os, sys, datetime, time, praw, pymongo
from praw.handlers import MultiprocessHandler

m = pymongo.MongoClient('mongodb://localhost:27017/')
db = m['reddit_sample']

reddit_id_list = []

def get_wait_time():
  query = db.metadata.find_one({'wait_time': {'$exists':True}})
  if query == None:
    print 'Error, no entry for wait_time found in reddit_sample.metadata'
    exit()
  else:
    return query['wait_time']
	
def utc_now():
  return (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()

def update_submission(post):
  entry = db.active_datasets.find_one( {'id': post.id}, {'finish_time':True, 'history':True} )
  if entry == None:
    print 'Error, post wasn\'t in our database for some reason!'
    exit()
  history = entry['history']
  current_time = utc_now()
  history.append( (current_time, post.score, post.num_comments) )
  
  if current_time >= entry['finish_time']:  # Retire the entry if its experiment is complete
    if db.datasets.find_one({'id': post.id}) != None:   # If somehow our data has already been completed, forget it
      db.active_datasets.remove( {'id': post.id} )
      return 0
    complete_entry = db.active_datasets.find_one( {'id': post.id} )
    complete_entry['history'] = history
    del complete_entry['finish_time']
    db.active_datasets.remove( {'id': post.id} )
    db.datasets.insert( complete_entry )
  else:
    db.active_datasets.update( {'id': post.id}, {'$set': { 'history': history}} )
  
  return abs( history[len(history)-2][1] - post.score )
  

if __name__ == '__main__':
  # Stage 0: Connect to reddit and our database
  print '\n'
  r = praw.Reddit('Reddit sampling experiment: update_data.py v/0.1.', handler = MultiprocessHandler())
 
  while True:   
    reddit_id_list = []
    delta_score = 0
    num_entries = 0
    print 'Polling database...',
    for entry in db.active_datasets.find({}, {'id':True}):
      reddit_id_list.append('t3_' + entry['id'])
      num_entries += 1
    print 'updating', num_entries, 'reddit posts...',
    for post in r.get_submissions(reddit_id_list):
      delta_score += update_submission(post)
    wait_time = get_wait_time()
    print 'delta of', delta_score, '; Sleeping for', wait_time/60.0, 'minutes.'
    time.sleep(wait_time)
