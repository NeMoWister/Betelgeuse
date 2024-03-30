import sqlite3
import datetime


class SchedulerManager:
    def __init__(self, db_name: str = 'scheduler.db'):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    # def __enter__(self):
    #     self.connection = sqlite3.connect(self.db_name)
    #     self.cursor = self.connection.cursor()
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, traceback):
    #     self.connection.close()

    def create_thematic_day(self, channel_id: int, date: str, thematic_day_subject: str) -> None:
        """Создаёт тематический день

        :param channel_id: id сервера
        :param date: дата в формате YYYY-MM-DD
        :param thematic_day_subject: тема тематического дня
        """
        self.cursor.execute(
            'INSERT OR REPLACE INTO thematic_day (server_id, thematic_day_date, thematic_day_subject) VALUES (?, ?, ?)',
            (channel_id, date, thematic_day_subject))
        self.connection.commit()

    def delete_thematic_day(self, channel_id: int, date: str) -> None:
        """Удаляет тематический день

        :param channel_id: id сервера
        :param date: дата в формате YYYY-MM-DD
        """
        self.cursor.execute(
            'DELETE FROM thematic_day WHERE server_id=? AND thematic_day_date=?',
            (channel_id, date))
        self.connection.commit()

    def get_thematic_timetable(self, server_id: int):
        """Возвращает расписание тематических дней

        :param server_id: id сервера
        :return: список кортежей (дата, тема)
        """
        self.cursor.execute(
            'SELECT thematic_day_date, thematic_day_subject FROM thematic_day WHERE server_id=?',
            (server_id,))
        return self.cursor.fetchall()
        start_date = datetime.date.today().strftime("%Y-%m-%d")
        end_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        self.cursor.execute(
            'SELECT thematic_day_date FROM thematic_day WHERE server_id=? AND thematic_day_date BETWEEN ? AND ?',
            (server_id, start_date, end_date))
        results = self.cursor.fetchall()
        return [result[0] for result in results]

    def get_thematic_day(self, channel_id: int) -> str:
        """Возвращает тему тематического дня

        :param channel_id: id сервера
        :return: str: тема тематического дня
        """
        self.cursor.execute(
            'SELECT thematic_day_subject FROM thematic_day WHERE server_id=? AND thematic_day_date=?',
            (channel_id, datetime.date.today().strftime('%Y-%m-%d')))
        return self.cursor.fetchone()[0] if not None else ''

    def auto_delete_thematic_day(self) -> None:
        """Удаляет тематические дни старше 7 дней

        :return: None
        """
        period_to_delete = datetime.date.today() - datetime.timedelta(days=7)
        self.cursor.execute(
            'DELETE FROM thematic_day WHERE thematic_day_date < ?',
            (period_to_delete.strftime('%Y-%m-%d'), ))
        self.connection.commit()

    def create_schedule_timetable_record(self, server_id: int, post_hour: int, channel_id: int) -> None:
        """Создаёт расписание сервера

        :param server_id: id сервера
        :param post_hour: время в часах
        :param channel_id: id канала
        :return: None"""
        self.cursor.execute(
            'INSERT OR REPLACE INTO timetable (server_id, post_hour, channel_id) VALUES (?, ?, ?)',
            (server_id, post_hour, channel_id))
        self.connection.commit()

    def delete_server(self, server_id: int):
        """Удаляет расписание сервера

        :param server_id: id сервера
        :return: None
        """
        self.cursor.execute(
            'DELETE FROM timetable WHERE server_id=?',
            (server_id, ))
        self.connection.commit()

    def get_schedule_timetable(self) -> list:
        """Возвращает список серверов, у которых есть посты в данный час

        :return: list: список id серверов
        """

        time = datetime.datetime.now().hour
        self.cursor.execute(
            'SELECT server_id FROM timetable WHERE post_hour=?',
            (time, )
        )
        results = self.cursor.fetchall()
        return [result[0] for result in results]

    def get_channel_id_by_server(self, server_id: int):
        """Возвращает id канала, в который нужно отправлять пост

        :param: server_id: id сервера
        :return: int: id канала"""
        self.cursor.execute('SELECT channel_id FROM timetable WHERE server_id=?', (server_id, ))
        result = self.cursor.fetchone()[0]
        return result

    def get_schedule(self) -> dict:
        """Возвращает пару (id сервера, тема тематического дня) в виде словаря

        :return: dict: словарь с id сервера и темой тематического дня
        """
        server_list = self.get_schedule_timetable()
        result = {}
        for item in server_list:
            result[item] = self.get_thematic_day(item)
        return result
