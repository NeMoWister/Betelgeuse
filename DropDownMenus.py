import discord


class Dropdown(discord.ui.Select):
    def __init__(self, data):
        self.data = None
        # Set the options that will be presented inside the dropdown

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose your favourite colour...', min_values=1, max_values=1, options=data)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(f'Your favourite colour is {self.values[0]}')
        self.data = self.values[0]


class DropdownView(discord.ui.View):
    def __init__(self, data):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(data))
