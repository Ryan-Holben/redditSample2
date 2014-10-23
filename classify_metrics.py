# Various metrics to be applied to a score vs. time dataset, for the purpose of quantifying successful posts.

def convergence(slope, factor):
  """Returns the point at which the dataset converges, which we define to be a point after which no major features occur.
  We find this by multiplying the max slope by the factor, and ask: After what point does the slope no longer exceed this?
  The factor should be a percentage, ie factor = 0.1 means the slope has reduced to 10% for the remainder of the dataset."""

  cutoff = max([x[1] for x in slope]) * factor
  i = len(slope)-1
  while i > 0:
    if abs(slope[i][1]) <= cutoff:
      i -= 1
    else:
      break
  return i
  
def moving_avg(dataset, n):
  """Returns a dataset which has been smoothed via a moving average.
  Looks n places on either side of each point, where n is a positive integer."""
  # data = [dataset[0] for i in range(n)] + dataset + [dataset[len(dataset)-1] for i in range(n)]
  # result = []
  # for i in range(n, len(dataset) + n):
  #   # I can't use the exact moving average definition; my points are not equadistant!
  #   result.append( sum(data[i-n:i+n])/(2*n+1) )
  # return result
  #
  if n == 0: return dataset
  data = [dataset[0][1] for i in range(n)] + [d[1] for d in dataset] + [dataset[len(dataset)-1][1] for i in range(n)]
  result = []
  for i in range(n, len(dataset) + n):
    # I can't use the exact moving average definition; my points are not equadistant!
    result.append( [dataset[i-n][0], sum(data[i-n:i+n])/(2*n+1)] )
  return result
  