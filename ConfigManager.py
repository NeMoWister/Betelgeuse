import json
import os


# class Bot_Config:
#     def __init__(self, server_id, name, path, chance, cache):
#         self.server_id = server_id
#         self.name = name
#         self.path = path
#         self.chance = chance
#         self.cache = cache


class BotConfigManager:
    def __init__(self, config_folder: str = 'config/'):
        self.config_folder = config_folder

    def get_default_config(self) -> json:
        # to do
        # custom config for every server
        """Загрузка дефолтного конфига
        :return: json
        """

        with open(f'{self.config_folder}default/config.json', 'r', encoding='utf-8') as file:
            return json.load(file)

    def edit_config(self, server_id: int, data: json) -> None:
        """Редактирование конфига сервера
        :param server_id:
        :param data:
        :return: None
        """
        with open(f'{self.config_folder}{server_id}/config.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)

    def load_config(self, server_id: int = 0) -> json:
        """Загрузка конфига по id сервера
        :param server_id:
        :return: json
        """
        try:
            with open(f'{self.config_folder}{server_id}/config.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(e)
            return self.get_default_config()

    def delete_config(self, server_id: int) -> None:
        """"Удаление конфига по id сервера
        :param server_id:
        :return: None"""
        os.remove(f'{self.config_folder}{server_id}')
