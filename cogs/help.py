# -*- coding: utf-8 -*-
import disnake, asyncio
import json
from disnake.ext import commands

config = json.load(open('config.json', 'rb'))
color = config['color']
prefix = "v!"
embeds = {"Защита":f'`{prefix}whitelist [Пользователь | ID]` - Добавить пользователя в вайтлист\n\n\
`{prefix}antibot` - Банить не верифицированых ботов\n\n\
`{prefix}save` - Сохранить сервер\n\n\
`{prefix}backup` - Сделать бэкап сервера',
                
"Модерация":f"`{prefix}ban [пользователь] [причина]` - Забанить пользователя\n\n\
`{prefix}kick [пользователь] [причина]` - Кикнуть пользователя\n\n\
`{prefix}unban [пользователь]` - Разбанить пользователя\n\n\
`{prefix}clear [количество сообщений]` - Очистить определёное количество сообщений\n\n\
`{prefix}mute [пользователь]` - Выдать мут пользователю\n\n\
`{prefix}unmute [пользователь]` - Снять мут с пользователя\n\n\
`{prefix}warn [пользователь] [причина]` - Выдать предупреждение пользователю\n\n\
`{prefix}unwarns [пользователь]` - Снять все предупреждение с пользователя\n\n\
`{prefix}warns` - Посмотреть предупреждение пользователя\n\n\
`{prefix}massban [пользователи] [причина]` - Забанить сразу несколько пользователей\n\n\
`{prefix}unwarn [пользователь | ID]` - Снять предупреждение с пользователя\n\n\
`{prefix}cooldown [секунд]` - Установить задержку для чата\n\n\
`{prefix}lock` - Забрать у всех права писать в чат\n\n\
`{prefix}unlock` - Выдать всем права писать в чат",

"Владелец":f"`{prefix}delspamroles`- Удалить спам роли\n\n\
`{prefix}delspamchannels` - Удалить спам каналы\n\n\
`{prefix}delchan` - Удалить все каналы\n\n\
`{prefix}delroles` - Удалить все роли\n\n\
Данные команды может использовать исключительно владелец сервера",

"Логи":f"`{prefix}log_channel [Канал | ID]` - Включить оповещение действий в определёный канал",

"Настройка":f"`{prefix}ignore_channel [Канал | ID]` - Игнорируемые каналы для последующих параметров\n\n\
`{prefix}antilink` - Запретить отправлять ссылки.\n\n\
`{prefix}auto_reg_ban [дни]` - Банить новых пользователей при входе, регистрация которых меньше 30 дней, или ваше значение\n\n\
`{prefix}leaveban` - Если пользователь покидает сервер, ему автоматически даётся бан\n\n\
`{prefix}autorole [Роль | ID]` - Начальная роль при входе\n\n\
`{prefix}whitelisted` - Показать пользователей, которые в вайтлисте",

"Информация":f"`{prefix}info [Пользователь]` - Информация про: [`@Пользователя`; `#Канал`; `:Эмодзи`]\n\n\
`{prefix}server_info` - Информация о сервере"
        }
class Dropdown(disnake.ui.Select):
    def __init__(self):

        options = [
            disnake.SelectOption(
                label="Защита", description="Команды защиты", emoji="💻"
            ),
            disnake.SelectOption(
                label="Модерация", description="Команды модерации", emoji="🎯"
            ),
            disnake.SelectOption(
                label="Настройка", description="Настройки вашего сервера", emoji="⚙"
            ),
            disnake.SelectOption(
                label="Логи", description="Логирование вашего сервера", emoji="🔗"
            ),
            disnake.SelectOption(
                label="Владелец", description="Команды для владельца", emoji="💎"
            ),
            disnake.SelectOption(
                label="Информация", description="Команды информации", emoji="📱"
            )
        ]
        super().__init__(
            placeholder="Меню помощи",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(
                    embed = disnake.Embed(
                            title = f":gear: | {self.values[0]}",
                            description = f">>> **{embeds[self.values[0]]}**",
                            color = color
                        )
            )



class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def help(self, ctx, arg = None):
        if not arg:
            view = disnake.ui.View()
            view.add_item(Dropdown())
            await ctx.send(embed = disnake.Embed(
                    title = ":gear: | Помощь",
                    description = f"""
Используйте свитч внизу, или пишите вручную команды ниже:


`{ctx.prefix}{ctx.command}` - Команды защиты
`{ctx.prefix}{ctx.command}` - Команды модерации
`{ctx.prefix}{ctx.command}` - Команды владельца
`{ctx.prefix}{ctx.command}` - Команды логов
`{ctx.prefix}{ctx.command}` - Настройки

[🔗Добавить бота](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot)
                    """,
                    color = int(color)
                ), view = view)
        else:
            try:
                await ctx.send(embed = disnake.Embed(
                        title = f":gear: | {arg.capitalize()}",
                        description = f">>> **{embeds[arg.lower()]}**",
                        color = int(color)
                    ))
            except:
                pass


def setup(bot):
    bot.add_cog(Help(bot))