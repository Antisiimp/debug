import disnake as disnake
import sqlite3, json
from disnake.ext import commands


class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.config = json.load(open('config.json','rb'))
		self.color = self.config['color']

	@commands.command(aliases = ['удал-спам-роли', 'delspamr', 'delsroles', 'delsr', 'dsr'])
	@commands.has_permissions(administrator = True)
	async def delspamroles(self, ctx):
		if int(ctx.author.id == ctx.guild.owner_id):
			list = []
			for channel in ctx.guild.roles:
				if channel.name in list:
					await channel.delete()
				else:
					list.append(channel.name)
			await ctx.send(embed = disnake.Embed(description = ">>> **Выполнено**", color = disnake.Colour(self.color)))
   
	@commands.command(aliases = ['удал-спам-каналы', 'delspamc', 'delspamch', 'delschannels', 'delsch', 'delsc', 'dsc'])
	@commands.cooldown(1, 30, commands.BucketType.default)
	@commands.has_permissions(administrator = True)
	async def delspamchannels(self, ctx):
		list = []
		if int(ctx.author.id == ctx.guild.owner_id):
			for channel in ctx.guild.channels:
				if channel.name in list:
					await channel.delete()
				else:
					list.append(channel.name)
			await ctx.send(embed = disnake.Embed(description = ">>> **Выполнено**", color = disnake.Colour(self.color)))
   
   @commands.command(aliases = ['удалить-спам-вебхуки', 'delspamw', 'delswebhooks', 'delsw', 'dsw'])
   @commands.cooldown(1, 30, commands.BucketType.default)
   async def delspamwebhooks(self, ctx):
       if int(ctx.author.id == ctx.guild.owner_id):
            list = []
        	for webhook in await channel.webhooks():
                if webhook.id == entry.target.id:
                    if webhook.id in list:
                    	await webhook.delete()
                    else:
                        list.append(webhook.id)
            await ctx.send(embed = disnake.Embed(description = ">>> **Выполнено**", color = disnake.Colour(self.color)))

def setup(bot):
	bot.add_cog(Owner(bot))
