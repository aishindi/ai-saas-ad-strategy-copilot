from cachetools import TTLCache

# Cache LLM responses for 10 minutes
prompt_cache = TTLCache(maxsize=200, ttl=600)


def get_cached_response(key):
    return prompt_cache.get(key)


def set_cached_response(key, value):
    prompt_cache[key] = value


def clear_cache():
    prompt_cache.clear()