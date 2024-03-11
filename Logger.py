from os import makedirs, path
from time import strftime


class BotLogger:
    def __init__(self):
        self.time = {'date': strftime("%Y_%m_%d"), 'time': strftime("%H_%M")}
        self.log_path = path.join('logs', self.time['date'])
        makedirs(self.log_path, exist_ok=True)

    def info(self, messages: list) -> None:
        """

        :param messages:
        :return:
        """
        with open(path.join(self.log_path, f'log_{self.time["time"]}.txt'), mode='w') as file:
            for line in messages:
                file.write(f'{line}\n')
