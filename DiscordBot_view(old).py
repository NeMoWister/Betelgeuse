import time
import typing

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select
from dotenv import load_dotenv
from os import getenv
import datetime

from SMTP import SmtpFeedback
from Logger import BotLogger
from DropDownMenus import DropdownView
from ConfigManager import BotConfigManager
from SchedulerManager import SchedulerManager
from ImageSelector import ImageSelector

configManager = BotConfigManager()
config_data = configManager.load_config()
imageSelector = ImageSelector(config_data)

load_dotenv()
token = getenv('token')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('ready')
    try:
        synced = await bot.tree.sync()
        print(synced)
    except Exception as e:
        print(e)


@bot.tree.command(name='settings', description="настройка сервера")
@app_commands.describe(post_every='Через какой промежуток времени постить?', post_hour='Время начала?')
async def config(interaction: discord.Interaction, post_hour: int, post_every: int):
    if interaction.user.guild_permissions.administrator:
        with SchedulerManager() as sm:
            try:
                sm.create_schedule_timetable_record(interaction.guild_id, post_hour, post_every, interaction.channel_id)
                await interaction.response.send_message('Успех', ephemeral=True)
            except Exception as e:
                print(e)
                await interaction.response.send_message('Не удалось', ephemeral=True)
        # await interaction.response.send_message(
        #     f'xyi {interaction.guild_id}, {interaction.channel_id}, {post_every}, {post_hour}',
        #     ephemeral=True)  # добавить BotModules
    else:
        await interaction.response.send_message(f'Вы не администратор, идите нахуй.', ephemeral=True)


# @bot.tree.command(name='send_feedback', description="отправить отзыв")
# @app_commands.describe(feedback_message='Сообщение')
# async def send_feedback(interaction: discord.Interaction, feedback_message: str):
#     with SmtpFeedback() as sf:
#         try:
#             sf.send_feedback(feedback_message, interaction.user.id)
#             await interaction.response.send_message('Успех', ephemeral=True)
#         except Exception as e:
#             print(e)
#             await interaction.response.send_message('Не удалось отправить фидбек, повторите позже', ephemeral=True)


async def theme_autocomplete(interaction: discord.Interaction, theme: str) -> typing.List[app_commands.Choice[str]]:
    data = []
    for choice_theme in config_data['anime_list']:
        if theme.lower() in choice_theme['name'].lower():
            data.append(app_commands.Choice(name=choice_theme['name'], value=choice_theme['name']))
    return data


@bot.tree.command(name='thematic_day', description="заказ тематического дня")
@app_commands.describe()
@app_commands.autocomplete(theme=theme_autocomplete)
async def thematic_day(interaction: discord.Interaction, theme: str, date: str):

    class MyView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.select_1 = discord.ui.Select(options=[discord.SelectOption(label=_['name']) for _ in config_data['anime_list']])
            self.select_1.callback = self.callback_1
            self.add_item(self.select_1)
            self.select_2 = discord.ui.Select(options=[discord.SelectOption(label=missing_date.replace('-', '.')) for missing_date in results])
            self.select_2.callback = self.callback_1
            self.add_item(self.select_2)

        async def callback_1(self, interaction: discord.Interaction):
            await interaction.response.defer()
            # do something

    with SchedulerManager() as sm:

        def get_missing_dates():
            today = datetime.date.today()
            end_of_week = today + datetime.timedelta(days=7)
            all_dates = [date.strftime("%d-%m") for date in
                         [today + datetime.timedelta(days=i) for i in range((end_of_week - today).days)]]
            dates_in_table = sm.get_thematic_timetable(interaction.guild_id)
            format_dates = [datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m") for date in dates_in_table]
            missing_dates = [date for date in all_dates if date not in format_dates]
            return missing_dates

        try:
            results = get_missing_dates()
        except Exception as e:
            print(e)

        view = MyView()

        await interaction.response.send_message(view=view, ephemeral=True)
        time.sleep(10)

        await interaction.followup.send(f'{view.select_1.values}, {view.select_2.values}')



    #
    #     try:
    #         sm.create_thematic_day(interaction.guild_id, datetime.datetime.strptime(select_dates.values[0].replace('.', '-'), '%d-%m').strftime('%Y-%m-%d'), select_theme.values[0])
    #     except Exception as e:
    #         print(e)


bot.run(token)
