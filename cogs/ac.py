import disnake
import json
import requests
import asyncio
import sqlite3
import io
import json


from disnake import *
from disnake import Forbidden
from datetime import datetime
from disnake.ext import commands
from disnake.ext.commands import *
from aiohttp import ClientSession


async def delChan(ctx):
	for channel in ctx.guild.channels:
		try:
			await channel.delete()
		except:
			pass

async def delRoles(ctx):
	for role in ctx.guild.roles:
		try:
			await role.delete()
		except:
			pass

async def delHooks(ctx):
    for webhook in await channel.webhooks():
        if webhook.id == entry.target.id:
            try:
                await webhook.delete()
            except:
                pass


async def deleteAll(ctx):
	await delChan(ctx)
	await delRoles(ctx)
    await delHooks(ctx)


def getColor(arg):
	return tuple(int(arg.strip('#')[i:i + 2], 16) for i in (0, 2, 4))

class ac(Cog):
	def __init__(self,bot):
		self.bot = bot
		self.data = sqlite3.connect('data.sqlite3', timeout=1)
		self.cursor = self.data.cursor()
		self.config = json.load(open('config.json','rb'))
		self.color = self.config['color']
  
	async def getRoles(self,ctx):
		return self.cursor.execute(f'SELECT name, position, color FROM rls WHERE id = {ctx.guild.id}').fetchall()


	async def getChannels(self, ctx, channelType):
		return self.cursor.execute("SELECT * FROM channels WHERE id = ? AND type = ?", (ctx.guild.id, str(channelType))).fetchall()



	async def checkUser(self, entry, guild):

		whitelist = self.cursor.execute("SELECT * FROM wl WHERE id = ? AND guild = ?", (entry.user.id, guild.id))
		if len(whitelist.fetchall()) > 0 or entry.user.id == guild.owner_id or entry.user.id == self.bot.user.id:
			return True

	async def notDependent(self,ctx):
		categories = await self.getChannels(ctx, 'category')
		Textchannels = await self.getChannels(ctx, 'text')
		Voicechannels = await self.getChannels(ctx, 'voice')
		Stagechannels = await self.getChannels(ctx, 'stage')
		Forumchannels = await self.getChannels(ctx, 'forum')

		for category in categories:

			try:
				await ctx.guild.create_category(name = category[1], position = category[2])
			except:
				pass

		for i in Textchannels:
			if not i[4]:
				await ctx.guild.create_text_channel(name = i[1], position = i[2])
		for i in Voicechannels:
			if not i[4]:
				await ctx.guild.create_voice_channel(name = i[1], position = i[2])
	async def dependentCategoryChannels(self, ctx):
		CatChannels = self.cursor.execute(f"SELECT * FROM channels WHERE id = {ctx.guild.id} AND cn IS NOT NULL").fetchall()
		for cat in ctx.guild.categories:
			for i in CatChannels:
				if i[4] == cat.name:
					if i[3] == 'text':
						await cat.create_text_channel(name = i[1], position = i[2])
					else:
						await cat.create_voice_channel(name = i[1], position = i[2])
	async def createRoles(self, ctx):
		roles = await self.getRoles(ctx)
		#print(roles)
		for iteration in roles:
			print(iteration)
			color = getColor(iteration[2])

			role = await ctx.guild.create_role(name = iteration[0], colour = disnake.Color.from_rgb(color[0], color[1], color[2]))
			await role.edit(position = iteration[1])

	async def createEmojis(self, ctx):

		for i in self.cursor.execute(f"SELECT url FROM emojis WHERE id = {ctx.guild.id}"):
			with io.Bytes(requests.get(i[0]).read()) as file:
				await ctx.guild.create_custom_emoji(image = file)


	@commands.command(aliases = ['bu'])
	@commands.cooldown(1, 30, commands.BucketType.default)
	@commands.has_permissions(administrator = True)
	async def backup(self, ctx):

		view = disnake.ui.View()
		for i in [disnake.ui.Button(label = "Конечно", style = disnake.ButtonStyle.blurple, emoji = '♻', custom_id = 'da'), disnake.ui.Button(label = "Нет, не надо", style = disnake.ButtonStyle.danger, emoji = '⛔', custom_id = 'net')]:
			view.add_item(i)

		await ctx.send(embed = disnake.Embed(title = ':gear: | Резервная копия сервера', description = f">>> **Перед востановлением, удалять все каналы/роли и тд:**",color = disnake.Colour(self.color)), view = view)

		inter = await self.bot.wait_for('button_click', check = lambda i: i.author == ctx.author)
		if inter.component.custom_id == 'da':
			await deleteAll(ctx)
		
		await self.notDependent(ctx)
		await self.dependentCategoryChannels(ctx)
		await self.createRoles(ctx)

	@commands.command()
	@commands.cooldown(1, 30, commands.BucketType.default)
	@commands.has_permissions(administrator = True)
	async def save(self, ctx):
		guild = ctx.guild
		self.cursor.execute("DELETE FROM channels WHERE id = {}".format(guild.id))
		self.cursor.execute("DELETE FROM rls WHERE id = {}".format(guild.id))
		filterchan = []
		for i in guild.categories:
			for c in i.channels:
				filterchan.append(c.id)
		for channel in ctx.guild.stage_channels:
			if not channel.id in filterchan:
				self.cursor.execute("INSERT INTO channels VALUES(?, ?, ?, ?, ?)", (guild.id, channel.name, channel.position, 'stage', None))
		for channel in ctx.guild.forum_channels:
			if not channel.id in filterchan:
				self.cursor.execute("INSERT INTO channels VALUES(?, ? , ?, ?, ?)", (guild.id, channel.name, channel.position, 'forum', None))
		for channel in ctx.guild.text_channels:
			if not channel.id in filterchan:
				self.cursor.execute("INSERT INTO channels VALUES(?, ?, ?, ?, ?)", (guild.id, channel.name, channel.position, 'text', None))
		for channel in ctx.guild.voice_channels:
			if not channel.id in filterchan:
				self.cursor.execute("INSERT INTO channels VALUES(?, ?, ?, ?, ?)", (guild.id, channel.name, channel.position, 'voice', None))	
		for category in guild.categories:
			for channel in category.text_channels:
				self.cursor.execute("INSERT INTO channels VALUES(?, ?, ?, ?, ?)", (guild.id, channel.name, channel.position, 'text', category.name))
			for channel in category.stage_channels:
				self.cursor.execute("INSERT INTO channels VALUES(?, ?, ?, ?, ?)", (guild.id, channel.name, channel.position, 'stage', category.name))
			for channel in category.forum_channels:
				self.cursor.execute("INSERT INTO channels VALUES(?, ?, ?, ?, ?)", (guild.id, channel.name, channel.position, 'forum', category.name))
			for channel in category.voice_channels:
				self.cursor.execute("INSERT INTO channels VALUES(?, ?, ?, ?, ?)", (guild.id, channel.name, channel.position, 'voice', category.name))
			self.cursor.execute("INSERT INTO channels VALUES(?, ?, ?, ?, ?)", (guild.id,category.name, category.position, 'category', None))
		for role in ctx.guild.roles:
			if role.is_bot_managed() or role.is_default():
				pass
			else:
				self.cursor.execute("INSERT INTO rls VALUES(?,?,?,?)", (guild.id, role.name, role.position, str(role.color)))

		for emoji in ctx.guild.emojis:
			self.cursor.execute("INSERT INTO emojis VALUES(? , ?)", (ctx.guild.id,emoji.url ) )
		self.data.commit()
		await ctx.send(embed = disnake.Embed(title = ':gear: | Сохранён',
		description = ">>> **Ваш сервер успешно сохранён.**",
		color = disnake.Colour(self.color)
		))

	@commands.command(aliases = ['wl'])
	@commands.cooldown(1, 5, commands.BucketType.default)
	@commands.has_permissions(administrator = True)
	async def whitelist(self,ctx, target:disnake.Member = None):
		if target and ctx.author.top_role.position > ctx.guild.me.top_role.position or ctx.author == ctx.guild.owner:
			member = target if type(target) ==disnake.Member else disnake.Object(target)
			view = disnake.ui.View()
			view.add_item(disnake.ui.Button(label = "Добавить", emoji = "♻", custom_id = "add", style = disnake.ButtonStyle.green))
			view.add_item(disnake.ui.Button(label = "Удалить", emoji = "⛔", custom_id = "remove",style = disnake.ButtonStyle.danger))
			view.add_item(disnake.ui.Button(label = "Отмена", emoji = "❌", custom_id = "cancel",style = disnake.ButtonStyle.blurple))
			message = await ctx.send(
				embed = disnake.Embed(
					title = "Подтверждение",
					description=f">>> **Вы уверены, что хотите добавить в вайтлист {member.name}? Ведь после этого, бот будет игнорировать все его действия на сервере?**",
					color = disnake.Colour(self.color)
				),view = view
			)
			inter = await self.bot.wait_for('Button_click', check = lambda i: i.author == ctx.author)
			if inter.component.custom_id == 'add':
				await message.edit(embed = disnake.Embed(title = ':gear: | Белый список',
					description = f">>> **Теперь все действия пользователя `{member.display_name}` игнорируются.**",
					color = disnake.Colour.green()
				),view = None)
				self.cursor.execute(f"DELETE FROM wl WHERE id = {member.id} AND guild = {ctx.guild.id}")
				self.cursor.execute("INSERT INTO wl VALUES(?, ?)", (ctx.guild.id, member.id))
				self.data.commit()

			elif inter.component.custom_id == 'remove':
				await message.edit(embed = disnake.Embed(title = ':gear: | Белый список',
					description = f">>> **Вы убрали пользователя `{member.display_name}` из белого списка**",
					color = disnake.Colour(self.color)
				),view = None)
				self.cursor.execute(f"DELETE FROM wl WHERE id = {member.id} AND guild = {ctx.guild.id}")
				self.data.commit()
			else:
				await message.delete()

			
	@commands.command(aliases = ['log-channel', 'logs', 'set-log', 'log'])
	@commands.cooldown(1, 5, commands.BucketType.default)
	@commands.has_permissions(administrator = True)
	async def log_channel(self, ctx, channel: disnake.TextChannel = None):
		if channel:
			view = disnake.ui.View()
			for i in [disnake.ui.Button(label = "Включить", emoji = "♻", custom_id = "add", style = disnake.ButtonStyle.green), disnake.ui.Button(label = "Выключить", emoji = "⛔", custom_id = "remove",style = disnake.ButtonStyle.danger), disnake.ui.Button(label = "Отмена", emoji = "❌", custom_id = "cancel",style = disnake.ButtonStyle.blurple)]:
				view.add_item(i)
			message = await ctx.send(
				embed = disnake.Embed(
					title = "Подтверждение",
					description=f">>> **Вы уверены, что хотите включить данную функцию?**",
					color = disnake.Colour(self.color)
				),view = view
			)
			inter = await self.bot.wait_for('Button_click', check=lambda i: i.author == ctx.author)
			if inter.component.custom_id == 'add':
				self.cursor.execute('DELETE FROM channel WHERE guild = {}'.format(ctx.guild.id))
				self.cursor.execute("INSERT INTO channel VALUES(?,?)", (channel.id, ctx.guild.id))
				await ctx.send(embed=disnake.Embed(title=":gear: | Логирование", description=f">>> **Канал добавлен в базу данных.**",color = disnake.Colour.green()), view = None)
				self.data.commit()
			elif inter.component.custom_id == 'remove':
				self.cursor.execute('DELETE FROM channel WHERE guild = {}'.format(ctx.guild.id))
				await message.edit(embed = disnake.Embed(title = ":gear: | Логирование",
					description = f">>> **Канал удалён из базы данных.**",
					color = disnake.Colour.red()), view = None)
				self.data.commit()
			else:
				await message.delete()
		

	@Cog.listener()
	async def on_ready(self):
		print("Anticrash is loaded")


	@Cog.listener()
	async def on_guild_channel_delete(self,channel):
		try:
			entry = await channel.guild.audit_logs(action = disnake.AuditLogAction.channel_delete, limit = 1).get()
			if await self.checkUser(entry, channel.guild):
				return
			else:
				await entry.user.ban(reason = 'Anti Channel Delete')
		except:
			pass

            
    @Cog.listener()
    async def on_guild_channel_create(self, channel):
        entry = await channel.guild.audit_logs(action = disnake.AuditLogAction.channel_create, limit = 1).get()
        if await self.checkuser(entry, channel.guild):
            return
        else:
            try:
                await entry.user.ban(reason='Anti Channel Create')
            except:
                pass
            try:
                await channel.delete()
            except:
                pass


	@Cog.listener()
	async def on_guild_role_delete(self, role):
		try:
			entry = await role.guild.audit_logs(action = disnake.AuditLogAction.role_delete, limit = 1).get()
			if await self.checkUser(entry, role.guild):
				return
			else:
				try: 
                    role = await role.guild.create_role(
                        name=role.name,
                        color=role.color,
                        hoist=role.hoist,
                        mentionable=role.mentionable,
                        permissions=role.permissions,
                        icon=role.icon
                        )
                    await role.edit(position=role.position)
                except:
                    pass
		except:
			pass

	
	@Cog.listener()
	async def on_member_remove(self, member):
		try:
			entry = await member.guild.audit_logs(action = disnake.AuditLogAction.kick,limit = 1).get()
			if await self.checkUser(entry, member.guild):
				return
			else:
				await entry.user.ban(reason = "Anti Member Kick")
		except:
			pass

	@Cog.listener()
	async def on_member_ban(self,guild, member):
		try:
			entry = await guild.audit_logs(action = disnake.AuditLogAction.ban, limit = 1).get()
			if await self.checkUser(entry, guild):
				return
			else:
				try:
					await entry.user.ban(reason = "Anti Member Ban")
     			try:
                    await member.unban()
                except:
                    pass
                inv = await guild.channels[0].create_invite()
                try:
                    embed = disnake.Embed(
                        title="Анти-краш система",
                        color=disnake.Color.red(),
                        description=f"Вы были забанены на сервере {ctx.guild.name}. Я предотвратил краш и разбанил вас."),
                    embed.add_field(
                        name=':link: Ссылка на сервер',
                        value=f'''>>> {inv}''')
                    await ctx.member.send(embed=embed)
                except:
                    pass
		except:
			pass

	@Cog.listener()
	async def on_guild_channel_update(self, before, after):
		try:
			entry = await after.guild.audit_logs(action=disnake.AuditLogAction.channel_update, limit=1).get()
			if await self.checkUser(after.guild ,entry ):
				return
			else:
				if isinstance(after, disnake.TextChannel):
        			if channel.category == None:
                        try:
                            await after.edit(
                                name=channel.name,
                                topic=channel.topic,
                                position=channel.position,
                                nsfw=channel.nsfw,
                                slowmode_delay=channel.slowmode_delay,
                                overwrites=channel.overwrites,
                            )
                        except:
                            pass
                    else:
                        try:
                            await after.edit(
                                name=channel.name,
                                topic=channel.topic,
                                position=channel.position,
                                nsfw=channel.nsfw,
                                slowmode_delay=channel.slowmode_delay,
                                overwrites=channel.overwrites,
                                category=disnake.utils.get(channel.guild.categories, name=channel.category.name)
                                )
                        except:
                            pass
                if isinstance(after, disnake.VoiceChannel):
                    if channel.category == None:
                        try:
                            await after.edit(
                                name=channel.name,
                                position=channel.position,
                                overwrites=channel.overwrites,
                                nsfw=channel.nsfw,
                                slowmode_delay=channel.slowmode_delay,
                                user_limit=channel.user_limit,
                                bitrate=channel.bitrate,
                                rtc_region=channel.rtc_region,
                                video_quality_mode=channel.video_quality_mode,
                                )
                        except:
                            pass
                    else:
                        try:
                            await after.edit(
                                name=channel.name,
                                position=channel.position,
                                overwrites=channel.overwrites,
                                nsfw=channel.nsfw,
                                slowmode_delay=channel.slowmode_delay,
                                user_limit=channel.user_limit,
                                bitrate=channel.bitrate,
                                rtc_region=channel.rtc_region,
                                video_quality_mode=channel.video_quality_mode,
                                category=disnake.utils.get(channel.guild.categories, name=channel.category.name)
                                )
                        except:
                            pass
                if isinstance(after, disnake.CategoryChannel):
                    try:
                        await after.edit(
                            name=channel.name,
                            position=channel.position,
                        	overwrites=channel.overwrites
                            )
                    except:
                        pass
                if isinstance(after, disnake.StageChannel):
                    if channel.category == None:
                        try:
                            await after.edit(
                                name=channel.name,
                                position=channel.position,
                                overwrites=channel.overwrites,
                                nsfw=channel.nsfw,
                                topic=channel.topic,
                                bitrate=channel.bitrate,
                                user_limit=channel.user_limit,
                                rtc_region=channel.rtc_region,
                                video_quality_mode=channel.video_quality_mode,
                                slowmode_delay=channel.slowmode_delay,
                                requesting_to_speak=channel.requesting_to_speak,
                                )
                        except:
                            pass
                    else:
                        try:
                            await after.edit(
                                name=channel.name,
                                position=channel.position,
                                overwrites=channel.overwrites,
                                nsfw=channel.nsfw,
                                topic=channel.topic,
                                bitrate=channel.bitrate,
                                user_limit=channel.user_limit,
                                rtc_region=channel.rtc_region,
                                video_quality_mode=channel.video_quality_mode,
                                slowmode_delay=channel.slowmode_delay,
                                requesting_to_speak=channel.requesting_to_speak,
                                category=disnake.utils.get(channel.guild.categories, name=channel.category.name)
                                )
                        except:
                            pass
                if isinstance(after, disnake.ForumChannel):
                    if channel.category == None:
                        try:
                            await after.edit(
                                name=channel.name,
                                position=channel.position,
                                overwrites=channel.overwrites,
                                nsfw=channel.nsfw,
                                topic=channel.topic,
                                auto_archive_duration=channel.auto_archive_duration,
                                slowmode_delay=channel.slowmode_delay,
                                thread_slowmode_delay=channel.default_thread_slowmode_delay,
                                sort_order=channel.sort_order,
                            	layout=channel.layout,
                                default_reaction=channel.default_reaction,
                                available_tags=channel.available_tags,
                                requires_tag=self.flags.require_tag,
                                )
                        except:
                            pass
                    else:
                        try:
                            await after.edit(
                                name=channel.name,
                                position=channel.position,
                                overwrites=channel.overwrites,
                                nsfw=channel.nsfw,
                                topic=channel.topic,
                                auto_archive_duration=channel.auto_archive_duration,
                                slowmode_delay=channel.slowmode_delay,
                                thread_slowmode_delay=channel.thread_slowmode_delay,
                                sort_order=channel.sort_order,
                                layout=channel.layout,
                                default_reaction=channel.default_reaction,
                                available_tags=channel.available_tags,
                                requires_tag=self.flags.require_tag,
                                category=disnake.utils.get(channel.guild.categories, name=channel.category.name)
                                )
                        except:
                            pass
		except:
			pass

	@Cog.listener()
	async def on_guild_role_update(self, before, after):
		try:
			entry = await after.guild.audit_logs(action = disnake.AuditLogAction.role_update, limit = 1).get()
			if await self.checkUser(entry, after.guild):
				return
			else:
        		try:
                    await after.edit(
                        name=before.name,
                        color=before.color,
                        position=before.position,
                        hoist=before.hoist,
                        mentionable=before.mentionable,
                        permissions=before.permissions,
                        icon=before.icon
                        )
                except:
                    pass
		except:
			pass

	@Cog.listener()
	async def on_guild_update(self, before, after):
		try:
			entry = await after.guild.audit_logs(action = disnake.AuditLogAction.guild_update, limit = 1).get()
			if await self.checkUser(entry, after.guild):
				return
			else:
				if before.name != after.name:
					try:
						await after.edit(name=before.name)
					except:
						pass
				if before.icon != after.icon:
					try:
						await after.edit(icon=before.icon)
					except:
						pass

	@Cog.listener
    async def on_webhooks_update(self, channel):
        entry = await channel.guild.audit_logs(action = disnake.AuditLogAction.webhook_create, limit = 1).get()
        if await self.checkUser(entry, channel.guild):
            return
        else:
            try:
                await entry.user.ban(reason='Anti Webhook Create')
            except:
                pass
            for webhook in await channel.webhooks():
                if webhook.id == entry.target.id:
                    try:
                        await webhook.delete()
                    except:
                        pass


def setup(bot):
	bot.add_cog(ac(bot))