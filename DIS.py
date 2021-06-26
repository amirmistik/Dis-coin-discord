from discord import message, user
from discord import reaction
from discord import channel
from discord.ext import commands
import discord
import sqlite3

TOKEN = "ODU3NzA3OTA3NTMzMTExMzE2.YNTgvA.Jo7Wd656dJlnuAZURSONj9-aIRQ"

bot = discord.Client()

bot = commands.Bot(command_prefix='!')

#wallet
wallet = sqlite3.connect('wallet.db')
wal = wallet.cursor()

wal.execute("""CREATE TABLE IF NOT EXISTS wallet(
            user_id INT,
            crypto INT);
        """)
wallet.commit()

#transaction
transaction = sqlite3.connect('transaction.db')
trans = transaction.cursor()

trans.execute("""CREATE TABLE IF NOT EXISTS wallet(
            from_user INT,
            to_user INT,
            money INT);
        """)
transaction.commit()

class colors:
    default = 0
    teal = 0x1abc9c
    dark_teal = 0x11806a
    green = 0x2ecc71
    dark_green = 0x1f8b4c
    blue = 0x3498db
    dark_blue = 0x206694
    purple = 0x9b59b6
    dark_purple = 0x71368a
    magenta = 0xe91e63
    dark_magenta = 0xad1457
    gold = 0xf1c40f
    dark_gold = 0xc27c0e
    orange = 0xe67e22
    dark_orange = 0xa84300
    red = 0xe74c3c
    dark_red = 0x992d22
    lighter_grey = 0x95a5a6
    dark_grey = 0x607d8b
    light_grey = 0x979c9f
    darker_grey = 0x546e7a
    blurple = 0x7289da
    greyple = 0x99aab5

@bot.command(aliases=["создать", "кошелек"], brief="Создает кошелек", pass_context=True)
async def create(ctx):
    color = colors.gold
    user_id = ctx.message.author.id
    info = wal.execute('SELECT * FROM wallet WHERE user_id=?', (user_id, ))
    if info.fetchone() is None:
        balance = 1
        wal.execute("INSERT INTO wallet VALUES(?,?);", (user_id, balance))
        wallet.commit()
        embed = discord.Embed(title='**ВЫ СОЗДАЛИ КОШЕЛЕК**', color=color)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='**У ВАС УЖЕ ЕСТЬ КОШЕЛЕК**', color=color)
        await ctx.send(embed=embed)

@bot.command(aliases=["передать", "дать", "give"], brief="Переводит коины", pass_context=True)
async def tip(ctx, to_user: discord.Member, money):
    color = colors.gold
    to = to_user.id
    frm = ctx.author.id
    money = int(money)
    wal.execute("""SELECT * from wallet where user_id = ?""", (frm,))
    record = wal.fetchone()
    if record is None:
        await ctx.message.author.send('🔴Вы не создали кошелек🔴')
    elif to == frm:
        await ctx.message.author.send('🔴Нельзя отправить самому себе🔴')
    elif money > record[1]:
        await ctx.message.author.send('🔴Недостаточно средств🔴')
    elif money <= 0:
        await ctx.message.author.send('🔴Число не должно быть меньше или равно 0🔴')
    elif money >= 5000:
        await ctx.message.author.send('🔴Слишком большое число🔴')
    elif money <= record[1] and record[0] != None:
        wal.execute("""SELECT * from wallet where user_id = ?""", (to,))
        record = wal.fetchone()
        if record is None:
            await ctx.message.author.send('🔴У пользователя которому вы хотите перевести нету кошелька🔴')
        else:
            wal.execute("""SELECT * from wallet where user_id = ?""", (frm,))
            record = wal.fetchone()
            #запись в бд
            trans.execute("INSERT INTO wallet VALUES(?,?,?)", (frm, to, money))
            transaction.commit()
            #тут отнимают у типера
            sql = """UPDATE wallet SET crypto = ? WHERE user_id = ?"""
            a = int(record[1]) - money
            wal.execute(sql, (a, int(record[0])))
            wallet.commit()
            #тут перевод
            wal.execute("""SELECT * from wallet where user_id = ?""", (to,))
            record = wal.fetchone()
            b = int(record[1]) + money
            wal.execute(sql,(b, int(record[0])))
            wallet.commit()
            embed = discord.Embed(title='**ПЕРЕВОД УСПЕШЕН**',description=f'**ОТ {ctx.author.name} К {to_user.name} {money} DIS**', color=color)
            await ctx.send(embed=embed)

@bot.command(aliases=["баланс", "bal"], brief="Узнать баланс", pass_context=True)
async def balance(ctx):
    color = colors.gold
    error = discord.Embed(title='**ОШИБКА**',description=f'**СОЗДАЙТЕ КОШЕЛЕК**', color=color)
    try:
        user_id = ctx.message.author.id
        wal.execute("""SELECT * from wallet where user_id = ?""", (user_id,))
        record = wal.fetchone()
        error = discord.Embed(title='**ОШИБКА**',description=f'**СОЗДАЙТЕ КОШЕЛЕК**', color=color)
        complete = discord.Embed(title='**БАЛАНС🔓**', description=f'**DIS:{record[1]}**', color=color)
        if record is None:
            await ctx.send(embed=error)
        else:
            await ctx.send(embed=complete)
    except:
        await ctx.send(embed=error)

@bot.command(aliases=["капитализация", "капа"], brief="Узнать капитализацию", pass_context=True)
async def cap(ctx):
    color = colors.gold
    wal.execute("""SELECT SUM(crypto) FROM wallet""")
    record = wal.fetchone()
    embed = discord.Embed(title='ОБЩАЯ КАПИТАЛИЗАЦИЯ',description=f'{record[0]}', color=color)
    await ctx.send(embed=embed)


@bot.command(aliases=["история", "транзакции"], brief="Посмотреть историю транзакций", pass_context=True)
async def history(ctx):
    await ctx.send(file=discord.File(r'transaction.db'))
    embed = discord.Embed(title='КАК ПОСМОТРЕТЬ',description=f'https://sqlitebrowser.org/dl/', color=colors.gold)
    await ctx.send(embed=embed)


@bot.command(aliases=["инфо", "помощь"], brief="Узнать о DIS", pass_context=True)
async def info(ctx):
    embed = discord.Embed(title='КАКИЕ ПЛЮСЫ', description=f'**1.Необязательно быть на сервере\n2.Все транзакции записываются\n3.Ограниченая эмиссия\n4.Быстрые транзакции\n5.Прозрачная система\n6.Скидки на товары\n7.Раздачи\n8.Расшифровка \nD - Diamond\nI - intelligent\nS - System**', color=colors.gold)
    await ctx.send(embed=embed)


@bot.command(aliases=["Топ","Богачи"], brief="Посмотреть самых богатых", pass_context=True)
async def top(ctx):
    wal.execute("SELECT crypto FROM wallet ORDER BY crypto DESC")
    money = wal.fetchall()
    wal.execute("SELECT user_id FROM wallet ORDER BY crypto DESC")
    users = wal.fetchall()
    print(money)
    if len(money) <= 3:
        await ctx.message.author.send('Слишком мало участников создали свои кошельки')
    else:
        print(users)
        first = await bot.fetch_user(users[0][0].split('#')[0])
        second = await bot.fetch_user(users[1][0].split('#')[0])
        third = await bot.fetch_user(users[2][0].split('#')[0])
        embed = discord.Embed(title='ТОП 3 БОГАЧА', description=f'1){first} {money[0][0]} DIS\n2){second} {money[1][0]} DIS\n3){third} {money[2][0]} DIS', color=colors.gold)
        await ctx.message.author.send(embed=embed)

bot.run(TOKEN)
