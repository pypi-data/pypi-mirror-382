-- KEYS[1] = zset_key (failures zset)
-- KEYS[2] = hash_key (meta hash)
-- ARGV[1] = member_id
-- ARGV[2] = score (timestamp as integer seconds)
-- ARGV[3] = cutoff_score (timestamp before which to delete)
-- ARGV[4] = reason
-- ARGV[5] = meta_ttl_seconds (optional, 0 means no expire)


redis.call('ZADD', KEYS[1], ARGV[2], ARGV[1])
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[3])
local count = redis.call('ZCARD', KEYS[1])
redis.call('HSET', KEYS[2], 'last_failure_reason', ARGV[4], 'last_failure_ts', ARGV[2], 'count', tostring(count))
if tonumber(ARGV[5]) > 0 then
    redis.call('EXPIRE', KEYS[1], ARGV[5])
    redis.call('EXPIRE', KEYS[2], ARGV[5])
end
return count