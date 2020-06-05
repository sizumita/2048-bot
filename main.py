import discord
from game import Game2048
import asyncio


client = discord.Client()


async def send_image(channel, game):
    return await channel.send(file=discord.File(fp=game.generate_mass_bytes(), filename='2048.png'))


@client.event
async def on_message(message):
    if not message.content.startswith('!2048'):
        return
    ch = message.channel
    banmen = None
    if message.content == '!2048 edit':
        await ch.send('盤面を送信してください')
        msg = await client.wait_for('message', check=lambda m: m.author.id == message.author.id and m.channel.id == message.channel.id, timeout=60)
        banmen = list(map(lambda x: list(map(int, x.split())), msg.content.split('\n')))
    game = Game2048(client, None, banmen)
    before = await send_image(ch, game)
    before2 = None
    while game.has_0():
        before2 = await ch.send('入力をどうぞ')
        try:
            msg = await client.wait_for('message', check=lambda m: m.author.id == message.author.id and m.channel.id == message.channel.id and m.content in ['w', 'a', 's', 'd', 'q'], timeout=60)
        except Exception:
            return
        content = msg.content
        if content == 'q':
            await ch.send('終了')
            return
        if content == 'w':
            game.up()
        if content == 'a':
            game.left()
        if content == 's':
            game.down()
        if content == 'd':
            game.right()
        game.set_2()
        await before.delete()
        await before2.delete()
        before = await send_image(ch, game)
    await ch.send('負け。')

client.run('')

