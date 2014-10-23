library(rmongodb)
m <- mongo.create()
print(mongo.get.database.collections(m, 'reddit_sample'))
buf <- mongo.bson.buffer.create()
#mongo.bson.buffer.start.object(buf, "experiment_time")
#mongo.bson.buffer.append(buf, "$exists", TRUE)
#mongo.bson.buffer.finish.object(buf)
query <- mongo.bson.from.buffer(buf)

cur <- mongo.find(m, 'reddit_sample.datasets', query=query)
history <- value <- NULL
framelist <- NULL
i <- 1
val1 <- val2 <- 0
entry1 <- entry2 <- 0
while (mongo.cursor.next(cur)) {
  value <- mongo.cursor.value(cur)
  history <- mongo.bson.value(value, 'history')
  df <- data.frame(matrix(unlist(history), nrow=length(history), byrow=T))
  df[[1]] = df[[1]] - df[[1]][1]   # Makes the first datapoint correspond with t = 0
  if(val2 < max(df[[2]])) {         # Helps us find interesting data by finding successful posts
    val1 <- val2
    val2 <- max(df[[2]])
    entry1 <- entry2
    entry2 <- i
  }
  framelist[[i]] <- df
  i <- i + 1
}

# plot(framelist[[601]][ , c(1,2)])
# 601, 1529, 506