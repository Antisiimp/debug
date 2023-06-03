import disnake
import sqlite3
import requests
import os
import json
from disnake.ext import commands
import keep_alive
config = json.load(open('config.json','rb'))
dev_ids = [857682987272896532]


keep_alive.keep_alive()
class Bot(commands.Bot):

	def __init__(self):

		super().__init__(
			command_prefix = 'v!',
			intents = disnake.Intents.all(),
			help_command = None
			)
		self.data = sqlite3.connect('data.sqlite3', timeout=1)
		self.cursor = self.data.cursor()


	async def on_ready(self):
		print("Bot is ready. Logged as ", self.user)
		members = 0
		"""		for i in list(map(lambda guild: len(guild.members), self.guilds)):
			members += i"""

		mems = 0
		for i in list(map(lambda guild: len(guild.members), self.guilds)):
			mems += i
		print(f"Юзеров: {mems}\nГильдий: {len(self.guilds)}")
      
		#self.cursor.execute("CREATE TABLE IF NOT EXISTS ")

		stat=disnake.Streaming(
        	name=f"Guilds: {len(self.guilds)} | v!help",
        	url="https://www.twitch.tv/vulture",
    	)


		await self.change_presence(activity=stat)

		for file in os.listdir('./cogs'):
			if file.endswith('.py'):
				self.load_extension(f"cogs.{file[:-3]}")

		self.data.commit()
	async def on_guild_remove(self, guild):
		self.cursor.execute(f"DELETE FROM channels WHERE id = {guild.id}")
		self.cursor.execute(f"DELETE FROM rls WHERE id = {guild.id}")
		self.cursor.execute(f"DELETE FROM channel WHERE guild = {guild.id}")


		self.data.commit()

	async def on_command(self, ctx):
		try:
			requests.post(
				url = "https://discord.com/api/webhooks/1094153304654757940/_Yk6DaPUGr8tRoZ68ML6dgHqZMnJOc4pVIrSoh5tiaeyGi04XFNOhufaRUHHANNoAMWX",
				json = {
					"content":"",
					"username":"",
					"embeds":[
						{
							"title": f"{ctx.prefix}{ctx.command}",
							"description":f"**Сервер: `{ctx.guild.name}` | `{ctx.guild.id}`\n\nКанал: `{ctx.channel.name}` | `{ctx.channel.id}`\n\nАвтор: `{ctx.author.name}` | `{ctx.author.id}`\n\nВладелец: `{ctx.guild.owner}` | `{ctx.guild.owner_id}`**\n\nУчастников: `{len(ctx.guild.members)}`",
							"color":0xc27c0e
						}
					]
				}
			)
		except:
			pass
	async def on_command_error(self, ctx, error):
		if type(error) == commands.MissingPermissions:
			await ctx.send(embed = disnake.Embed(title = ':gear: | Упс...',
				description = f">>> **Похоже у вас нет прав, чтоб использовать эту команду**",
				color = disnake.Colour(config['color'])))
		if type(error) == commands.CommandNotFound:
			await ctx.send(embed = disnake.Embed(title = '❌ | 404',
				description = f">>> **Проверьте правильность написанной команды и попробуйте еще раз**",
				color = disnake.Colour(config['color'])))
		if type(error) == commands.CommandOnCooldown:
			await ctx.send(embed = disnake.Embed(title = "💤 | Медленнее...",
				description = f">>> **Перед следующим использованием команды, подождите `{round(error.retry_after, 1)} секунд`**",
				color = disnake.Colour(config['color'])))
		if type(error) == disnake.Forbidden:
			await ctx.send(embed = disnake.Embed(title = "💨 | Нет прав",
				description = f">>> **Бот не может выполнить данное действие, из-за недостатка прав**",
				color = disnake.Colour(config['color'])))
		if type(error) == disnake.errors.NotFound:
			await ctx.send("Нет такого...")
		if type(error)== commands.MissingRequiredArgument:
			return
		else:
			try:
				requests.post(
					url = "https://discord.com/api/webhooks/953784060860313703/Za6SvnDOBgHYe1BFzvzvC2HABaiz94zex4KIVLI4PU_K3MWQPKSOUnaBrclitxPue1je",
					data = {'content':f"`{ctx.prefix}{ctx.command}` -> {error}"}
				)
			except:
				pass  


bot = Bot()

@bot.event
async def on_guild_join(guild):
    embed = disnake.Embed(
            title = f'💜 | Спасибо, что выбрали Vulture!',
            description = f'🚀 **Быстрый старт** \n`1.` Убедитесь, что у меня есть права администратора\n `2.` Переместите мою роль как можно выше, чтобы все мои функции работали правильно \n `3.` Изучите мои команды: `v!help` \n 🔗**Ссылки:** \n>>> [Дискорд сервер](https://discord.gg/Xxcjydsawt)',
            color = 0x71368a
        )
    await guild.text_channels[0].send(embed=embed)

@bot.command(aliases = ['сказать', 'Сказать', 'Say'])
async def say(ctx, *, msg: str = None):
    global dev_ids
    if not ctx.author.id in dev_ids:
        return await ctx.send(embed = disnake.Embed(title=':x:Доступ запрещен', description=f'Вы не являетесь разработчиком бота', colour = 0xf00a0a))
    await ctx.send(embed = disnake.Embed(description = msg))


  

@bot.command(brief = "private", description = "Создаёт приглашение, и отправляет его")
async def invite(ctx=None, id=None):
  g = bot.get_guild(int(id))
  if not g: return await ctx.send('Сервер не найден')
  for x in g.text_channels:
      link = await x.create_invite(max_age=100, max_uses=100)
      link = str(link)
      await ctx.send(link)
      return link
      await ctx.send(f'Нет прав для создания приглашения')

@bot.command(aliases = ['Ping', 'пинг', 'Пинг'])
async def ping(ctx):
    ping = bot.ws.latency
    message = await ctx.send('Пожалуйста, подождите. . .')
    await message.edit(embed = disnake.Embed(title='Понг', description=f'`{ping * 1000:.0f} ms` :ping_pong:', colour = 0x0059ff))

@bot.command(aliases = ['bot-info', 'Бот-Инфо', 'бот-инфо', 'инфо-бот', 'Инфо-Бот', 'Инфо-бот', 'info'])
async def infobot(ctx):
		embed = disnake.Embed(
			title = 'Информация обо мне',
			description = """
**Меня зовут `Vulture`**\n ```Я создан,чтобы защищать сервера от рейдеров и крашеров``` \n **Мой префикс:** `v!` \n **Команда помощи** `v!help` """,
			colour = 15105570)
		embed.add_field(
			name = '**Разработчики**',
			value = '<@857682987272896532>')
		embed.add_field(
			name = 'База данных',
			value = '`Sqlite3`',
			inline = True)
		embed.add_field(
			name = 'Пригласить меня',
			value = f'[Клик](https://discord.com/api/oauth2/authorize?client_id=1090683815963398194&permissions=8&scope=bot)',
			inline = True)
		embed.add_field(
			name = 'Сервер поддержки',
			value = '[Клик](https://discord.gg/Xxcjydsawt)',
			inline = True)
		embed.set_footer(
			text = 'Все права защищены | Vulture',
			icon_url = 'https://cdn.discordapp.com/avatars/1090683815963398194/c2269adbc7e4504e124ec0ae1f2c4589.png?size=512')
		await ctx.message.add_reaction('✅')
		await ctx.send(embed=embed)

TOKEN = os.environ.get("TOKEN")
bot.run(os.environ['TOKEN'])