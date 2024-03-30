import typing

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from os import getenv
import datetime
import asyncio

from SMTP import SmtpFeedback
from Logger import BotLogger
from ConfigManager import BotConfigManager
from SchedulerManager import SchedulerManager
from ImageSelector import ImageSelector

configManager = BotConfigManager()
config_data = configManager.load_config()
sm = SchedulerManager()

load_dotenv()
token = getenv('token')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


async def background_process(server_id: int, theme: str) -> None:
    """Получает id сервера и отправляет рандомные изображения

    :param server_id: id сервера
    :param theme: тема или категория изображений(конфигурирется в config.json)
    :return: None"""
    channel = bot.get_channel(sm.get_channel_id_by_server(server_id))

    image_selector = ImageSelector(config_data, theme)
    logger = BotLogger()

    out = image_selector.select_images()
    logger.info(out)
    await channel.send(files=[discord.File(file) for file in out])


def time_until_next_hour() -> int:
    """Возвращает время до начала следующего часа
    :return: int: количество секунд до следующего часа
    """
    now = datetime.datetime.now()
    next_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    _time_until_next_hour = next_hour - now
    return _time_until_next_hour.total_seconds()


@bot.event
async def on_ready():
    print('ready')
    try:
        synced = await bot.tree.sync()
        while True:
            current_timetable = sm.get_schedule()
            for server_id, theme in current_timetable.items():
                await background_process(server_id, theme)

            await asyncio.sleep(time_until_next_hour())
    except Exception as e:
        print(e)


@bot.tree.command(name='settings', description="настройка сервера")
@app_commands.describe(post_every='Через какой промежуток времени постить?', post_hour='Время начала?')
async def config(interaction: discord.Interaction, post_hour: int, post_every: int):
    if interaction.user.guild_permissions.administrator:
        try:
            for _ in range(0, 5):
                sm.create_schedule_timetable_record(interaction.guild_id, (post_hour + _ * post_every), interaction.channel_id)
            await interaction.response.send_message('Успех', ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message('Неудача', ephemeral=True)
    else:
        await interaction.response.send_message(f'Вы не администратор, идите нахуй.', ephemeral=True)


@bot.tree.command(name='send_feedback', description="отправить отзыв")
@app_commands.describe(feedback_message='Сообщение')
async def send_feedback(interaction: discord.Interaction, feedback_message: str):
    with SmtpFeedback() as sf:
        try:
            sf.send_feedback(feedback_message, interaction.user.id)
            await interaction.response.send_message('Успех', ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message('Не удалось отправить фидбек, повторите позже', ephemeral=True)


async def theme_autocomplete(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    data = []
    for choice_theme in config_data['anime_list']:
        if current.lower() in choice_theme['name'].lower():
            data.append(app_commands.Choice(name=choice_theme['name'], value=choice_theme['name']))
    return data


async def date_autocomplete(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
    data = []

    def get_missing_dates():
        today = datetime.date.today()
        end_of_week = today + datetime.timedelta(days=7)
        all_dates = [date.strftime("%d-%m-%Y") for date in
                     [today + datetime.timedelta(days=i) for i in range((end_of_week - today).days)]]
        dates_in_table = sm.get_thematic_timetable(interaction.guild_id)
        format_dates = [datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y") for date in dates_in_table]
        missing_dates = [date for date in all_dates if date not in format_dates]
        return missing_dates

    try:
        results = get_missing_dates()
        for missing_date in results:
            if current.lower() in missing_date.replace('-', '.'):
                data.append(
                    app_commands.Choice(name=missing_date.replace('-', '.'), value=missing_date.replace('-', '.')))
    except Exception as e:
        print(e)

    return data


@bot.tree.command(name='thematic_day', description="заказ тематического дня")
@app_commands.describe()
@app_commands.autocomplete(theme=theme_autocomplete, date=date_autocomplete)
async def thematic_day(interaction: discord.Interaction, theme: str, date: str):

    theme_validation = await theme_autocomplete(interaction, theme)
    date_validation = await date_autocomplete(interaction, date)

    if theme_validation and date_validation:

        try:
            sm.create_thematic_day(interaction.guild_id, str(datetime.datetime.strptime(date.replace('.', '-'), '%d-%m-%Y').strftime('%Y-%m-%d')), theme)
            await interaction.response.send_message(f'Тематический день запланирован на {date}', ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message('Неудача', ephemeral=True)

    else:
        await interaction.response.send_message('Введите нормальные данные', ephemeral=True)


bot.run(token)
