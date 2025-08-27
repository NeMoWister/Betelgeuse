from hashlib import md5
import os
import pickle
import random
from collections import deque

CACHE_FOLDER_PATH = "caches"

os.makedirs(CACHE_FOLDER_PATH, exist_ok=True)


def get_cache_path(object_path):
    hash_object = md5(object_path.encode())
    hash_str = hash_object.hexdigest()
    return os.path.join(CACHE_FOLDER_PATH, f"cache_{hash_str}.pkl")


def load_cache(object_path, max_cache_len):
    cache_path = get_cache_path(object_path)
    try:
        with open(cache_path, "rb") as cache_file:
            return pickle.load(cache_file)
    except FileNotFoundError:
        return deque(maxlen=max_cache_len)
    except Exception as e:
        print(f"Ошибка при загрузке кеша для {object_path}: {e}")
        return deque(maxlen=max_cache_len)


def save_cache(object_path, cache):
    cache_path = get_cache_path(object_path)
    try:
        with open(cache_path, "wb") as cache_file:
            pickle.dump(cache, cache_file)
    except Exception as e:
        print(f"Ошибка при сохранении кеша для {object_path}: {e}")


def start_posting(data):
    choice = random.choices(data['object_list'], weights=[item['chance'] for item in data['object_list']], k=1)[0]
    # print(choice)

    files = os.listdir(choice['path'])

    if choice['cache'].lower() == 'auto':
        total_files = len(files)
        max_cache_size = int(0.9 * total_files) if total_files > 100 else int(0.9 * total_files) - 11
    else:
        max_cache_size = choice['cache']

    cache = load_cache(choice['path'], max_cache_size)

    out = []

    while len(out) != 10:
        file = choice['path'] + '/' + random.choice(files)

        if file not in out and file not in cache and os.path.isfile(file):
            out.append(file)

    while len(cache) > max_cache_size - 10:
        cache.popleft()

    cache.extend(out)

    save_cache(choice['path'], cache)

    return [choice['name'], out]
