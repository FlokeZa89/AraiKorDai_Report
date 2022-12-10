# Bot Module
import interactions
from interactions import Button , ButtonStyle, ActionRow
import datetime
import pytz
from dotenv import load_dotenv
import os
import database_worker
from discord.ext import tasks
import asyncio
# import profile_genarator

# GET TOKEN
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = interactions.Client(TOKEN)

guild_ids = [798448521287434280]

def removemake(auid):
    rm = auid[auid.find('@')+1:auid.find('>')]
    buid = rm.lstrip("!")
    return buid


@bot.event
async def on_ready():
    await bot.change_presence(interactions.ClientPresence(status=interactions.StatusType.ONLINE,activities=[interactions.PresenceActivity(name="with Arai Kor Dai Server",details="with Arai Kor Dai Server",type=interactions.PresenceActivityType.GAME)]))
    members = await interactions.get(bot, interactions.Channel, object_id=1051088869703024730)
    guild = await interactions.get(bot,interactions.Guild,object_id=798448521287434280)
    await members.modify(name="╰✦ MEMBERS : {}".format(guild.member_count))

@tasks.loop(hours=3)
async def updatedate():
    datech = await interactions.get(bot, interactions.Channel, object_id=1051070646341345301)
    datex = datetime.datetime.now(pytz.timezone('Asia/Bangkok'))
    date = datex.strftime("%d %B %Y")
    await asyncio.sleep(1)
    await datech.modify(name="╭✦ {}".format(date))

@tasks.loop(minutes=30)
async def updatetime():
    members = await interactions.get(bot, interactions.Channel, object_id=1051088869703024730)
    guild = await interactions.get(bot,interactions.Guild,object_id=798448521287434280)
    await members.modify(name="╰✦ MEMBERS : {}".format(guild.member_count))


@bot.command(
    name="hidepublicchat",
    description="ตั้งค่าการมองเห็นแชทเซิฟเวอร์",
    scope=guild_ids,
)
async def settingchat(ctx: interactions.CommandContext):
    req_role = [1048099693252575242]
    user = ctx.author
    tguid = ctx.member.roles 
    role_public = await interactions.get(bot, interactions.Role, object_id=1048099693252575242)
    if any(req in tguid for req in req_role):
        await ctx.send(f"ช่องสาธารณะไม่ถูกซ่อนอีกต่อไป",ephemeral = True)
        await user.remove_role(role_public)
    else:
        await ctx.send(f"ช่องสาธารณะถูกซ่อนแล้ว",ephemeral = True)
        await user.add_role(role_public)


@bot.command(
    name="invite",
    description="รับลิงค์เชิญเข้าเซิฟเวอร์ Arai Kor Dai",
    scope=guild_ids,
)
async def invite(ctx: interactions.CommandContext):
    await ctx.send(f"ลิงค์เชิญเข้าสู่เซิฟ Arai Kor Dai : https://discord.gg/g5aKhQvgnM",ephemeral = True)

@bot.command(
    name="register",
    description="สมัครสมาชิกเพื่อเริ่มต้นใช้งาน",
    scope=guild_ids,
)
async def reg(ctx: interactions.CommandContext):
    status = database_worker.register(disid=ctx.member.user.id,disname=ctx.member.user.username)
    if (status == "true"):
        await ctx.send(f"นําข้อมูลเข้าระบบเรียบร้อย ^-^")
    else:
        await ctx.send(f"มีข้อมูลในระบบแล้ว ไม่จําเป็นต้องพิมพ์คําสั่งนี้แล้วล่ะ uwu",ephemeral = True)

@bot.command(
    name="getdiscordid",
    description="ดู UserID ดิสคอร์ด",
    scope=guild_ids,
)
async def getdiscordid(ctx: interactions.CommandContext):
    userid = str(ctx.member.user.id)
    await ctx.send(userid,ephemeral=True)

@bot.command(
    name="admin_reverse",
    description="Admin Tools: ย้อนกลับธุรกรรม",
    scope=guild_ids,
    options = [
        interactions.Option(
            name="trans_id",
            description="ID ของธุรกรรม",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def reverse_transaction(ctx, trans_id: int):
    uid = str(ctx.member.user.id)
    if (uid == "426967208082669598"):
        status = database_worker.reverse_transaction(trans_id)
        if(status == "true"):
            await ctx.send(f"Admin Tools : การดำเนินการสำเร็จ - รายการธุรกรรมนี้ย้อนกลับสำเร็จแล้ว")
        else:
            await ctx.send(f"Admin Tools : การดำเนินการถูกปฎิเสธ - รายการธุรกรรมนี้ถูกย้อนกลับไปแล้ว",ephemeral = True)
    else:
        await ctx.send("Admin Tools : Permission Denied",ephemeral = True)

@bot.command(
    name="transfer",
    description="โอนเงินจากบัญชีของคุณไปยังบัญชีปลายทาง",
    scope=guild_ids,
    options = [
        interactions.Option(
            name="mention",
            description="Mention ไปหาปลายทาง",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def transaction(ctx, mention: str):
    
    global from_id,to_id,fdata,tdata
    from_id = str(ctx.member.user.id)
    to_id = str(mention)
    from_id = from_id.lstrip("!")
    to_id = removemake(to_id)
    modal = interactions.Modal(title="ดำเนินการธุรกรรมของคุณ",custom_id="transaction",components=[(interactions.TextInput(style=interactions.TextStyleType.SHORT,
    label="(สำคัญ!) ตรวจสอบยอดเงิน ก่อนกด 'ส่ง' ทุกครั้ง",
    placeholder="ใส่จำนวนเงินที่จะโอนไปยังปลายทาง",
    custom_id="transaction_data",
    min_length=1,
    max_length=10,))],
    )
    fdata = database_worker.getdata(from_id)
    tdata = database_worker.getdata(to_id)
    if(fdata == () or tdata == ()):
        await ctx.send("การดำเนินการโอนเงิน (ถูกยกเลิก) : เนื่องจาก - ไม่พบบัญชีต้นทาง/ปลายทาง".format(from_id, to_id))
    else:
        if(from_id == to_id):
            await ctx.send("การดำเนินการโอนเงิน (ถูกยกเลิก) : เนื่องจาก - บัญชีปลายทางเป็นบัญชีเดียวกับต้นทาง".format(from_id, to_id))
        else:
            await ctx.popup(modal)
            await ctx.send("การดำเนินการโอนเงิน : จาก <@{}> ไปยัง <@{}> ".format(from_id, to_id),ephemeral = True)

@bot.modal("transaction")
async def modal_response(ctx, response: str):
    await ctx.send("ยืนยันจำนวนเงินสำเร็จ",ephemeral = True)
    error = database_worker.transaction(from_id,to_id,fdata,tdata,response)
    if (error == "true"):
        await ctx.send("การดำเนินการโอนเงิน : จำนวน {} Dollars Samlore / สถานะ - สำเร็จ".format(response))
    if (error == "numerror"):
        await ctx.send("การดำเนินการโอนเงิน (ถูกปฎิเสธ) : เนื่องจาก - ยอดเงินที่จะโอนมีอาจค่าติดลบ")
    if (error == "restricted"):
        await ctx.send("การดำเนินการโอนเงิน (ถูกปฎิเสธ) : เนื่องจาก - บัญชีต้นทางถูกระงับ")
    if (error == "notverify"):
        await ctx.send("การดำเนินการโอนเงิน (ถูกปฎิเสธ) : เนื่องจาก - บัญชีต้นทางยังไม่ได้รับการยืนยัน")
    if (error == "monerr"):
        await ctx.send("การดำเนินการโอนเงิน (ถูกปฎิเสธ) : เนื่องจาก - ยอดเงินของบัญชีต้นทางมียอดเงินไม่เพียงพอ")

@bot.command(
    name="point",
    description="เรียกดูยอดเงินคงเหลือ",
    scope=guild_ids,
)
async def data(ctx: interactions.CommandContext):
    data = database_worker.getdata(ctx.member.user.id)
    if (data != "false"):
        cdata = data[0]
        if (cdata[4] == "a"):
            await ctx.send("ยอดเงินในบัญชี : ไม่จำกัด Dollars Samlore")
        else:    
            await ctx.send("ยอดเงินในบัญชี : {:,} araikordai coin".format(cdata[2]))
    else:
        await ctx.send(f"ไม่พบข้อมูลในระบบ ใช้คําสั่ง /register ก่อนเพื่อใช้งานฟีเจอร์นี้",ephemeral = True)

@bot.command(
    name="โอนเงินเข้าบัญชีผู้ใช้นี้",
    scope=guild_ids,
    type=interactions.ApplicationCommandType.USER
)
async def transaction(ctx):
    global from_id,to_id,fdata,tdata
    from_id = str(ctx.member.user.id)
    to_id = str(ctx.target.user.id)
    modal = interactions.Modal(title="ดำเนินการธุรกรรมของคุณ",custom_id="transaction",components=[(interactions.TextInput(style=interactions.TextStyleType.SHORT,
    label="(สำคัญ!) ตรวจสอบยอดเงิน ก่อนกด 'ส่ง' ทุกครั้ง",
    placeholder="ใส่จำนวนเงินที่จะโอนไปยังปลายทาง",
    custom_id="transaction_data",
    min_length=1,
    max_length=10,))],
    )
    fdata = database_worker.getdata(from_id)
    tdata = database_worker.getdata(to_id)
    if(fdata == () or tdata == ()):
        await ctx.send("การดำเนินการโอนเงิน (ถูกยกเลิก) : เนื่องจาก - ไม่พบบัญชีต้นทาง/ปลายทาง".format(from_id, to_id))
    else:
        if(from_id == to_id):
            await ctx.send("การดำเนินการโอนเงิน (ถูกยกเลิก) : เนื่องจาก - บัญชีปลายทางเป็นบัญชีเดียวกับต้นทาง".format(from_id, to_id))
        else:
            await ctx.popup(modal)
            await ctx.send("การดำเนินการโอนเงิน : จาก <@{}> ไปยัง <@{}> ".format(from_id, to_id),ephemeral = True)

@bot.modal("transaction")
async def modal_response(ctx, response: str):
    await ctx.send("ยืนยันจำนวนเงินสำเร็จ",ephemeral = True)
    error = database_worker.transaction(from_id,to_id,fdata,tdata,response)
    if (error == "true"):
        await ctx.send("การดำเนินการโอนเงิน : จำนวน {} Dollars Samlore / สถานะ - สำเร็จ".format(response))
    if (error == "numerror"):
        await ctx.send("การดำเนินการโอนเงิน (ถูกปฎิเสธ) : เนื่องจาก - ยอดเงินที่จะโอนมีอาจค่าติดลบ")
    if (error == "restricted"):
        await ctx.send("การดำเนินการโอนเงิน (ถูกปฎิเสธ) : เนื่องจาก - บัญชีต้นทางถูกระงับ")
    if (error == "notverify"):
        await ctx.send("การดำเนินการโอนเงิน (ถูกปฎิเสธ) : เนื่องจาก - บัญชีต้นทางยังไม่ได้รับการยืนยัน")
    if (error == "monerr"):
        await ctx.send("การดำเนินการโอนเงิน (ถูกปฎิเสธ) : เนื่องจาก - ยอดเงินของบัญชีต้นทางมียอดเงินไม่เพียงพอ")

@bot.command(
    type=interactions.ApplicationCommandType.USER,
    name="สะกิดผู้ใช้นี้ (5)",
    scope=guild_ids,
    
)
async def shake(ctx):
    req_role = [863211744083836970,1043010105228136469]
    tguid = ctx.member.roles
    if any(req in tguid for req in req_role):
        for i in range(0, 5):
            curchan = await ctx.get_channel()
            rchannel = await interactions.get(bot, interactions.Channel, object_id=1043001872681799801)
            await ctx.target.modify(guild_id=798448521287434280,channel_id=rchannel)
            await ctx.target.modify(guild_id=798448521287434280,channel_id=curchan)
    else:
        await ctx.send(f"Access Denied",ephemeral = True)

@bot.command(
name="profile",
description="ดูโปรไฟล์ของคุณในเซิฟ",
scope=guild_ids,
)
async def embed(ctx: interactions.CommandContext):
    embed = interactions.Embed(timestamp=datetime.datetime.now(pytz.timezone('Asia/Bangkok')))
    data = database_worker.getdata(ctx.author.id)
    if (data != "false"):
        try:
            cdata = data[0]
            if cdata != ():
                if cdata[4] == "a":
                    rank = "ผู้ดูแลระบบ"
                    point = "ไม่จำกัด"
                if cdata[4] == "m":
                    rank = "สมาชิกทั่วไป"
                    point = cdata[3]
            else:
                point = "Disabled"
                rank = "Unknown"
        except:
            point = "Disabled"
            rank = "Unknown"
    if (data == "false"):
        point = "Disabled"
        rank = "Unknown"
    embed.set_author(name=str(ctx.member.user.username + "#" + ctx.member.user.discriminator), icon_url=ctx.author.get_avatar_url())
    embed.set_thumbnail(url=ctx.author.get_avatar_url())
    embed.add_field(name="Discord ID:", value="`{}`".format(str(ctx.author.id)), inline=True)
    if str(ctx.author.id) == "426967208082669598": embed.add_field(name="เข้าร่วมเซิฟเวอร์เมื่อ", value=ctx.member.joined_at.strftime("%d %B %Y")+"\n(ผู้ก่อตั้งเซิฟเวอร์)", inline=True)
    else: embed.add_field(name="เข้าร่วมเซิฟเวอร์เมื่อ", value=ctx.member.joined_at.strftime("%d %B %Y"), inline=True)
    embed.add_field(name="เงินในกระเป๋า", value=point, inline=True)
    embed.add_field(name="แรงค์", value=rank, inline=True)
    embed.set_footer(text="Araikordai Project | Google Link : In Development")
    await ctx.send(embeds=embed)

updatedate.start()

bot.start()