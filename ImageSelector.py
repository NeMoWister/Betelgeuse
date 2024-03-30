import json
import os
from hashlib import md5
from collections import deque
import pickle
from random import choices, choice


class ImageSelector:
    def __init__(self, data: json, mychoice=None):
        self.cache_path = "caches"
        os.makedirs(self.cache_path, exist_ok=True)
        self.data = data
        if mychoice is None:
            self.mychoice = choices(self.data['anime_list'], weights=[item['chance'] for item in self.data['anime_list']], k=1)[0]
        else:
            self.mychoice = [item for item in self.data['anime_list'] if item['name'] == mychoice][0]
        self.files = os.listdir(self.mychoice['path'])
        self.max_cache_size = int(0.9 * len(self.files)) if len(self.files) > 100 else int(0.9 * len(self.files)) - 11

    def get_cache_path(self, image_path: str) -> str:
        """Возвращает путь к кешу

        :param image_path: путь к файлу
        :return: str: путь к кешу"""
        # Генерируем уникальный путь для кеша на основе хэша пути
        hash_object = md5(image_path.encode())
        hash_str = hash_object.hexdigest()
        return os.path.join(self.cache_path, f"cache_{hash_str}.pkl")

    def load_cache(self, image_path: str, max_cache_len: int):
        """Загружает кеш из файла

        :param image_path: путь к файлу
        :param max_cache_len: максимальный размер кеша"""
        cache_path = self.get_cache_path(image_path)
        try:
            with open(cache_path, "rb") as cache_file:
                return pickle.load(cache_file)
        except FileNotFoundError:
            return deque(maxlen=max_cache_len)
        except Exception as e:
            print(f"Ошибка при загрузке кеша для {image_path}: {e}")
            return deque(maxlen=max_cache_len)

    def save_cache(self, image_path: str, cache: deque) -> None:
        """Сохраняет файл в кеш

        :param image_path: путь к файлу
        :param cache: кеш
        :return: None"""
        cache_path = self.get_cache_path(image_path)
        try:
            with open(cache_path, "wb") as cache_file:
                pickle.dump(cache, cache_file)
        except Exception as e:
            print(f"Ошибка при сохранении кеша для {image_path}: {e}")

    def select_images(self) -> list:
        """Возвращает список рандомно выбранных файлов

        :return: list: список файлов"""
        out = []
        cache = self.load_cache(self.mychoice['path'], self.max_cache_size)

        while len(out) != 10:
            # Составляем путь к файлу
            file = self.mychoice['path'] + '/' + choice(self.files)

            # Проверяем, что файл не находится в кеше и является допустимым файлом
            if file not in out and file not in cache and os.path.isfile(file):
                out.append(file)

        while len(cache) > self.max_cache_size - 10:
            cache.popleft()

        # Добавляем файлы в кеш
        cache.extend(out)

        # Удаляем старые значения, если кеш превысил максимальный размер

        # Сохраняем кеш после каждого вызова start_posting
        self.save_cache(self.mychoice['path'], cache)

        return out
