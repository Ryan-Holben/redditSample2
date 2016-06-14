RedditSample
========
<a href="/Data/post_slope.png"><img src="/Data/post_slopetn.png" align=right width="350px" alt="d/dt Score(t)"/></a>
The goal of this project is to analyze the score curves for posts on Reddit, to learn how popular and unpopular posts evolve over time.  Reddit was chosen as it has a nice API and a clear metric for a post's popularity.

### Running the experiment
We gather data over time using several independent threads.

1. `gather.py` Polls Reddit for new submissions.  As new submissions are detected, a corresponding entry is placed in the MongoDB collection `active_datasets` along with a finish_time value.
2. `update_data.py` Watches all entries in `active_datasets`, recording their scores at periodic intervals.  When an entry's lifetime has reached its finish_time, it is retired and moved to `datasets` collection.

### Analysis
Before the score curves can be analyzed, we have to clean the data.  Reddit introduces soft caps into scores in order to level the playing field between posts in popular vs unpopular subreddit communities.  Our first step is to detect and remove any score jumps due to soft caps, of which there may be multiple for a single posting.

<center>
<img src="/Data/capped.png" width="350px"> <img src="/Data/uncapped.png" width="350px">
</center>

Next, we use numerical methods to look at first and second derivatives for the posting curves.  We then sort posts by final score, and generate PDFs of their graphs.
