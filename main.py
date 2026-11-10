import os
import discord
from discord.ext import commands

# جلب التوكن من بيئة العمل في رايلواي
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    raise ValueError("خطأ: لم يتم العثور على متغير البيئة DISCORD_TOKEN.")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# استخدام بادئة التعجب (!) للأوامر العادية
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} successfully, N7Z-Bot is online with Prefix Commands & Strict Security!')

def check_admin_or_streamer(ctx) -> bool:
    is_admin = ctx.author.guild_permissions.administrator
    has_streamer_role = any(role.name.lower() in ["streamer", "ستريمر"] for role in ctx.author.roles)
    return is_admin or has_streamer_role

# ==========================================
# نظام الحماية الصارم (Anti-Exploit & Anti-Spam)
# ==========================================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # استثناء المشرفين والأدمن من نظام منع الروابط
    if message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return

    # منع الروابط والإعلانات والدعوات الخبيثة
    if "http://" in message.content or "https://" in message.content or "discord.gg/" in message.content:
        try:
            await message.delete()
            warning_msg = await message.channel.send(f"⚠️ {message.author.mention}, ممنوع إرسال الروابط أو الدعوات هنا!")
            await warning_msg.delete(delay=5)
        except Exception as e:
            print(f"Error handling link deletion: {e}")
        return

    await bot.process_commands(message)

@bot.event
async def on_guild_channel_delete(channel):
    print(f"⚠️ تنبيه أمني: تم حذف قناة {channel.name}")

@bot.event
async def on_guild_role_delete(role):
    print(f"⚠️ تنبيه أمني: تم حذف رتبة {role.name}")


# ==========================================
# الأوامر العادية (Prefix Commands)
# ==========================================

# 1. أمر البينغ (!ping)
@bot.command(name="ping", help="فحص سرعة استجابة البوت")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 البوت شغال وسريع وأمانه عالي! البينغ: `{latency}ms`")

# 2. أمر الحماية (!security)
@bot.command(name="security", help="حالة نظام الحماية والأمان الصارم في البوت")
async def security(ctx):
    embed = discord.Embed(
        title="🛡️ نظام الحماية الصارم نشط (Active)",
        description="• **منع الروابط والإعلانات:** مفعل تلقائياً.\n• **حماية السيرفر:** مراقبة الحذف والتخريب.\n• **حماية الأعضاء:** مؤمن بالكامل.",
        color=discord.Color.green()
    )
    embed.set_footer(text="N7Z-Bot Security System")
    await ctx.send(embed=embed)

# 3. أمر البرودكاست (!broadcast الرسالة)
@bot.command(name="broadcast", help="إرسال برودكاست لجميع الأعضاء بالخاص مع منشن في النهاية")
async def broadcast(ctx, *, message: str = None):
    if not check_admin_or_streamer(ctx):
        await ctx.send("❌ عذراً، أمر البرودكاست مخصص فقط لحاملي رتبة **Streamer** أو الإدارة!")
        return

    if not message:
        await ctx.send("❌ يرجى كتابة الرسالة المراد إرسالها بعد الأمر، مثال: `!broadcast السلام عليكم`")
        return

    status_msg = await ctx.send("⏳ جاري إرسال البرودكاست لجميع أعضاء السيرفر بالخاص...")

    success_count = 0
    fail_count = 0

    for member in ctx.guild.members:
        if member.bot:
            continue
        try:
            dm_text = f"{message}\n\n{member.mention}"
            await member.send(dm_text)
            success_count += 1
        except Exception:
            fail_count += 1

    await status_msg.edit(content=f"✅ تم إرسال البرودكاست بنجاح!\n📤 تم الإرسال إلى: `{success_count}` عضو\n❌ فشل الإرسال (مغلق الخاص): `{fail_count}` عضو")

# تشغيل البوت
if not DISCORD_TOKEN:
    print("خطأ: لم يتم العثور على متغير البيئة DISCORD_TOKEN!")
else:
    bot.run(DISCORD_TOKEN)
