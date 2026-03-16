from cachetools import TTLCache

prompt_cache = TTLCache(maxsize=100, ttl=300)


def get_cached_response(key):
    return prompt_cache.get(key)


def set_cached_response(key, value):
    prompt_cache[key] = value