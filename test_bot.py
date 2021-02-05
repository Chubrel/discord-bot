import discord
import asyncio

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def my_background_task(self):
        await self.wait_until_ready()
        counter = 0
        channel = self.get_channel(718956293259264006) # channel ID goes here
        print(channel)
        while not self.is_closed():
            counter += 1
            print(0)
            await channel.send(counter, )
            print(1)
            await asyncio.sleep(60) # task runs every 60 seconds

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        msg = message.content
        
        if msg == '&kill':
            if str(message.author) == 'Chubrel#9378':
                await message.channel.send('����� �������� ���!', )
                await message.channel.send('����������...', )
                await self.close()


client = MyClient()
with open('token.txt') as file:
    client.run(file.readline())
