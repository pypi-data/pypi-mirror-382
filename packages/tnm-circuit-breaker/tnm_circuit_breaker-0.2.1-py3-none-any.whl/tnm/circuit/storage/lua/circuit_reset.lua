-- KEYS[1] = zset_key
-- KEYS[2] = hash_key
-- ARGV[1] = ts
-- ARGV[2] = meta_ttl_seconds (optional, 0 means no expire)


redis.call('DEL', KEYS[1])
redis.call('HSET', KEYS[2], 'last_success_ts', ARGV[1], 'count', '0')
if tonumber(ARGV[2]) > 0 then
    redis.call('EXPIRE', KEYS[2], ARGV[2])
end
return 1