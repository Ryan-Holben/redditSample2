library(rmongodb)
m <- mongo.create()
print(mongo.get.database.collections(m, 'reddit_sample'))
buf <- mongo.bson.buffer.create()
query <- mongo.bson.from.buffer(buf)

cur <- mongo.find(m, 'reddit_sample.datasets', query=query)
history <- value <- NULL
framelist <- list()

mongo.cursor.next(cur)
mongo.cursor.next(cur)
value <- mongo.cursor.value(cur)
history <- mongo.bson.value(value, 'history')
df <- data.frame(matrix(unlist(history), nrow=length(history), byrow=T))

plot(df[,c(1,2)])
