import disnake

from disnake.ext import commands

from typing import Union

class Information(commands.Cog):

	def __init__(self, bot ):

		self.bot = bot

	@commands.command()
	async def info(self, ctx, argument:Union[disnake.User, disnake.Emoji, disnake.TextChannel, disnake.VoiceChannel, disnake.Role] = None):
		if isinstance(argument, disnake.User):
			embed = disnake.Embed(
							title = f":information_source: | {argument.name}",
							description = f">>> **ID: `{argument.id}`\n\nПользователь: `{argument.name}#{argument.discriminator}`\n\nДата создания: `{argument.created_at.strftime('%d/%m/%y')}`\n**",
							color = disnake.Colour.red()
						)
			embed.set_thumbnail(url=argument.avatar)
			await ctx.send(
					embed = embed
				)
		if isinstance(argument, disnake.Emoji):
			await ctx.send(
					embed = disnake.Embed(
							title = f":information_source: | {argument.name}",
							description = f">>> **ID: `{argument.id}`\n\n\
Упоминание: `<:{argument.name}:{argument.id}>`\n\n\
Анимированная: `{bool(argument.animated)}`\n\n\
Дата создания: `{argument.created_at.strftime('%d/%m/%y')}`\n\n\
Эмодзи: `{argument.name}`\n\n\
Ролей используют: `{len(argument.roles)}`\n\n\
Ссылка: {argument.url}**",
							color = disnake.Colour.green()
						)
				)
		if isinstance(argument, disnake.TextChannel) or isinstance(argument, disnake.VoiceChannel):
			await ctx.send(
					embed = disnake.Embed(
							title = f":information_source: | {argument.name}",
							description = f">>> **Канал: [`{argument.name}`]({argument.jump_url}) | `{argument.id}`\n\
Категория: `{argument.category}` | `{argument.category_id}`\n\n\
Дата создания: `{argument.created_at.strftime('%d/%m/%y')}`\n\n\
Пользователей, которые могут читать сообщения: `{len(argument.members)}`\n\n\
NSFW: `{'Вкл.' if bool(argument.nsfw) else 'Выкл.'}`\n\n\
Количество веток: `{len(argument.threads)}`\n\n\
Задержка: `{argument.slowmode_delay}`\n\n\
Описание: `{argument.topic}`**",
							color = disnake.Colour.red()
						)
				)
		if isinstance(argument, disnake.Role):
			await ctx.send(
					embed = disnake.Embed(
								title = f":information_source: | {argument.name}",
								description = f">>> **Роль: `{argument.name}` | `{argument.id}`\n\n\
Дата создания: `{argument.created_at.strftime('%d/%m/%y')}`\n\n\
Эмодзи: {str(argument.emoji) if argument.emoji else '`Нет`'}\n\n\
Участников с этой ролью: `{len(argument.members)}`\n\n\
Позиция роли: `{argument.position}`**",
								color = disnake.Colour.red()
						)
				)

def setup(bot):
	bot.add_cog(Information(bot))