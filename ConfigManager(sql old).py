import json
import sqlite3


class Bot_Config:
    def __init__(self, server_id, name, path, chance, cache):
        self.server_id = server_id
        self.name = name
        self.path = path
        self.chance = chance
        self.cache = cache


class BotConfigManager:
    def __init__(self, db_name: str = 'config_storage.db'):
        self.db_name = db_name

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS server_configs 
                            (id INTEGER PRIMARY KEY,
                            server_id INTEGER,
                            name TEXT,
                            path TEXT,
                            chance REAL
                            cache TEXT)''')
        self.connection.commit()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        self.connection.close()

    def save_config(self, server_id: int, data: str) -> None:
        self.cursor.execute('INSERT OR REPLACE INTO server_configs (server_id, config) VALUES (?, ?)', (server_id, json.dumps(data)))
        self.connection.commit()

    def load_config(self, server_id: int) -> Bot_Config:
        self.cursor.execute(f'SELECT config FROM server_configs WHERE server_id = {server_id}')
        result = self.cursor.fetchone()
        return Bot_Config(server_id=result[1], name=result[2], path=result[3], chance=result[4], cache=result[5]) if result else None


# def json_write(name, json_data):
#     with open(f"{name}.json", "w", encoding='utf-8') as json_file:
#         json.dump(json_data, json_file, ensure_ascii=False)
#
#
# def json_delete(name):
#     os.remove(f"{name}.json")
#
#
# def json_load(name):
#     with open(f"{name}.json", "r", encoding='utf-8') as json_file:
#         return json.load(json_file)
