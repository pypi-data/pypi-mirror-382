-- KEYS[1] = zset_key
-- ARGV[1] = cutoff_score
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1])
return redis.call('ZCARD', KEYS[1])