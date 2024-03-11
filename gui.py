import tkinter as tk
from tkinter import ttk
import subprocess
import ConfigManager


def on_button_click():
    value = int(entry.get())
    selected_anime = dropdown.get()
    selected_channel = dropdown2.get()

    if not selected_anime.lower() == 'рандом':
        anime_list_data = [next((anime for anime in data['anime_list'] if anime['name'].lower() == selected_anime.lower()), None)]
    else:
        anime_list_data = data['anime_list']
    channel_data = next((channel for channel in data['channel_id'] if channel['name'].lower() == selected_channel.lower()), None)

    new_data = {'anime_list': anime_list_data,
                'channel_id': [channel_data],
                'token': data['token'],
                "number_of_starts": value}

    config.json_write('temp', new_data)

    command = ["python", "DiscordBot.py", 'temp']
    subprocess.run(command)


root = tk.Tk()
root.title("GUI")

data = config.json_parse('config')

root.geometry("300x200")

root.resizable(width=False, height=False)

entry_label = tk.Label(root, text="Количество запусков:")
entry_label.pack()

entry = tk.Entry(root)
entry.pack()

dropdown_label = tk.Label(root, text="Выберите объект:")
dropdown_label.pack()

drop_list = [i['name'].capitalize() for i in data['anime_list']]
drop_list.append('Рандом')

dropdown = ttk.Combobox(root, values=drop_list[::-1])
dropdown.pack()

dropdown_label2 = tk.Label(root, text="Выберите канал:")
dropdown_label2.pack()

drop_list2 = [i['name'].capitalize() for i in data['channel_id']]


dropdown2 = ttk.Combobox(root, values=drop_list2)
dropdown2.pack()

button = tk.Button(root, text="Запустить", command=on_button_click)
button.pack()

root.mainloop()
