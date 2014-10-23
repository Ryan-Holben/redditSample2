import pymongo
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.fftpack import fft, ifft
import classify_metrics as metric

m = pymongo.MongoClient('mongodb://localhost:27017/')
db = m['reddit_sample']

# INDICATORS:
#
# Concave up vs concave down for some initial segment
#
# Jittery vs. smooth
#
# 

def slope(f):
  derivative = []
  x, y = [point[0] for point in f], [point[1] for point in f]
  for i in range(len(f)-1):
    derivative.append( [x[i], (y[i+1]-y[i])/(x[i+1]-x[i]) ])
  return derivative

def concavity(f):
  conc = []
  deriv = slope(f)
  x, y = [point[0] for point in deriv], [point[1] for point in deriv]
  for i in range(len(f)-2):
    conc.append( (x[i], (deriv[i+1][1]-deriv[i][1])/(x[i+1]-x[i])) )
  return conc

def quick_plot(dataset):
  plt.plot([x[0] for x in dataset], [x[1] for x in dataset])
def plot_graph(dataset):
  fig = plt.figure()
  #plt.plot(dataset)
  plt.plot([x[0] for x in dataset], [x[1] for x in dataset])
  return fig
  
def save_pdf(datasets, filename):
  pdf = PdfPages(filename)
  for d in datasets:
    pdf.savefig(plot_graph(d))
  pdf.close()

def filter(): #14000
  data = []
  for it in db.datasets.find():
    history = it['history']
    #if history[len(history)-1][0] - history[0][0] > 14000:
    if len(history) > 150:  # Isolate our 24 hour dataset
      start = history[0][0]
      for i in range(len(history)):
        history[i][0] -= start
      history[:0] = [ { k:it[k] for k in it.keys() if k != 'history'} ]  #[it['id']]
      data.append(history)
  return data
  
def get_maxes(data):
  for entry in data:
    entry[0:0] = [max([x[1] for x in entry[1:]])]
  return data
  
def get_bins_of_maxes(data):
  maxes = {}
  for entry in data:
    max = round(entry[0], -2)
    if max in maxes:
      maxes[max] += 1
    else:
      maxes[max] = 1
  plt.plot([x for x in maxes.keys()], [maxes[x] for x in maxes.keys()], 'bo')
  plt.show()
  
def get_experiment_times():
  lens = {}
  for it in db.datasets.find():
    history = it['history']
    length = round(history[len(history)-1][0] - history[0][0], 0)
    if length in lens:
      lens[length] += 1
    else:
      lens[length] = 1

  sort = sorted(lens, reverse = True)
  final = []
  for key in sort:
    final.append( (key, lens[key]) )
    
  plt.plot([x[0] for x in final], [x[1] for x in final], 'bo')
  plt.show()
  
def get_experiment_num_samples():
  nums = {}
  for it in db.datasets.find():
    history = it['history']
    n = len(it['history'])
    if n in nums:
      nums[n] += 1
    else:
      nums[n] = 1
      
  sort = sorted(nums, reverse = True)
  final = []
  for key in sort:
    final.append( (key, nums[key]) )
    
  plt.plot([x[0] for x in final], [x[1] for x in final], 'bo')
  plt.show()
  


def remove_soft_caps(dataset):
  deltas = []
  for i in range(len(dataset)-1):
    deltas.append(dataset[i+1][1] - dataset[i][1])
  jumps = []
  for i in range(len(deltas)):
    if deltas[i] <  -25:
      jumps.append(deltas[i])
    else:
      jumps.append(0)  
  sum = 0
  for i in range(len(jumps)):
    sum += jumps[i]
    dataset[i+1][1] -= sum
  return dataset

def smooth(data, num_frequencies):
  """Uses FFT to denoise a set of data."""
  frequencies = fft(data)
  high_pass = sorted(frequencies, key = abs, reverse=True)[:num_frequencies]
  denoised = []
  for f in frequencies:
    if f in high_pass:
      denoised.append(f)
    else:
      denoised.append(0)
  return ifft(denoised)

def save_processed_data(data, collection_name):
  collection = db[collection_name]
  for d in data:
    entry = { 'postdata': d[1], 'history': d[2:]}   # Package the data entry before storing it
    collection.insert(entry)
    
def load_processed_data(collection_name, num = 0):
  """Loads our pre-processed data.  If num is specified, loads that many entries, going from most to least popular."""
  data = []
  collection = db[collection_name]
  i = 0
  for it in collection.find():
    entry = it['history']
    entry[:0] = [ it['postdata'] ]
    data.append(entry)
    i += 1
    if num != 0 and i >= num:
      break
  return data

def store_subreddits():
  words = open('counts.txt').read().lower().split()
  subreddits = []
  i = 0
  while i in range(0, len(words)):
    subreddits.append((words[i], int(words[i+1])))
    i += 2
  db.metadata.insert({'subreddits':subreddits})
  
def load_subreddits():
  s = db.metadata.find_one({'subreddits': {'$exists': True}})['subreddits']
  
  def keyfunc(e):
     return e[1]
  return sorted(s, key=keyfunc, reverse=True)
  
if __name__ == '__main__':
  subreddits = load_subreddits()
  data = load_processed_data('processed', 200)
  for d in data:
    remove_soft_caps(d[1:])
    
  # s = slope(data[0][1:])
  # smoothed = smooth([x[1] for x in s], 100)             # Graph the smoothed slope
  # plt.plot([x[0] for x in s], [x[1] for x in s])
  # plt.show()
  # plt.plot([x[0] for x in s], smoothed)
  # plt.show()
  # exit()


  # s = slope(data[0][1:])
  # max_slope = max([x[1] for x in s])                    # Round the slope into bins
  # min_slope = min([x[1] for x in s])
  # BINS = 15
  # interval = (max_slope-min_slope)/BINS
  # for i in range(BINS):
  #   for x in s:
  #     if x[1] >= min_slope + i*interval and x[1] < min_slope + (i+1)*interval:
  #       x[1] = min_slope + i*interval
  # plt.plot([x[0] for x in s], [x[1] for x in s], 'ob')
  # plt.show()

  d = data[0][1:]
  # plt.subplot(211)
  # quick_plot(d)
  # plt.subplot(212)
  # avg = metric.moving_avg(d, 4)
  quick_plot(slope(d))
  quick_plot(slope(metric.moving_avg(d, 6)))
  quick_plot(metric.moving_avg(slope(d), 6))
  plt.show()
  exit()
  
  s = slope(d)
  # plt.plot(d[1:metric.convergence(s, 0.10)+1])
  # plt.show()
#  cpoint = metric.convergence(s, 0.10)
  quick_plot(d)
  quick_plot(d[0:metric.convergence(s, 0.1)+1])
  plt.show()
  exit()

  save_pdf( uncapped, 'uncapped_graphs.pdf' )
  save_pdf( [slope(d) for d in uncapped], 'slopes.pdf' )
  save_pdf( [concavity(d) for d in uncapped], 'concavities.pdf' )