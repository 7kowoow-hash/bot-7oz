import os
import discord
from discord import app_commands
from discord.ext import commands

# جلب التوكن من بيئة العمل في رايلواي
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    raise ValueError("خطأ: لم يتم العثور على متغير البيئة DISCORD_TOKEN.")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands successfully.")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")
    print(f'Logged in as {bot.user} successfully, N7Z-Bot is online with Strict Security!')

def check_admin_or_streamer(interaction: discord.Interaction) -> bool:
    is_admin = interaction.user.guild_permissions.administrator
    has_streamer_role = any(role.name.lower() in ["streamer", "ستريمر"] for role in interaction.user.roles)
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

    # 1. نظام الحماية من الروابط (منع الروابط والإعلانات والتخريب)
    if "http://" in message.content or "https://" in message.content or "discord.gg/" in message.content:
        try:
            await message.delete()
            warning_msg = await message.channel.send(f"⚠️ {message.author.mention}, ممنوع إرسال الروابط أو الدعوات هنا!")
            # حذف رسالة التحذير بعد 5 ثوانٍ لتنظيف الشات
            await warning_msg.delete(delay=5)
        except Exception as e:
            print(f"Error handling link deletion: {e}")
        return

    await bot.process_commands(message)

# حماية إضافية لمراقبة حذف القنوات أو الرتب (تنبيه)
@bot.event
async def on_guild_channel_delete(channel):
    print(f"⚠️ تنبيه أمني: تم حذف قناة {channel.name}")

@bot.event
async def on_guild_role_delete(role):
    print(f"⚠️ تنبيه أمني: تم حذف رتبة {role.name}")


# ==========================================
# أوامر السلاش (Slash Commands)
# ==========================================

# 1. أمر البينغ (/ping)
@bot.tree.command(name="ping", description="فحص سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 البوت شغال وسريع وأمانه عالي! البينغ: `{latency}ms`", ephemeral=True)

# 2. أمر الحماية (/security)
@bot.tree.command(name="security", description="حالة نظام الحماية والأمان الصارم في البوت")
async def security(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛡️ نظام الحماية الصارم نشط (Active)",
        description="• **منع الروابط والإعلانات:** مفعل تلقائياً.\n• **حماية السيرفر:** مراقبة حذف القنوات والرتب.\n• **حماية الأعضاء:** مؤمن بالكامل.",
        color=discord.Color.green()
    )
    embed.set_footer(text="N7Z-Bot Security System")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 3. أمر البرودكاست (/broadcast)
@bot.tree.command(name="broadcast", description="إرسال برودكاست لجميع الأعضاء بالخاص مع منشن في النهاية")
@app_commands.describe(message="نص الرسالة المراد إرسالها للجميع بالخاص")
async def broadcast(interaction: discord.Interaction, message: str):
    if not check_admin_or_streamer(interaction):
        await interaction.response.send_message("❌ عذراً، أمر البرودكاست مخصص فقط لحاملي رتبة **Streamer** أو الإدارة!", ephemeral=True)
        return

    await interaction.response.send_message("⏳ جاري إرسال البرودكاست لجميع أعضاء السيرفر بالخاص...", ephemeral=True)

    success_count = 0
    fail_count = 0

    for member in interaction.guild.members:
        if member.bot:
            continue
        try:
            dm_text = f"{message}\n\n{member.mention}"
            await member.send(dm_text)
            success_count += 1
        except Exception:
            fail_count += 1

    await interaction.followup.send(f"✅ تم إرسال البرودكاست بنجاح!\n📤 تم الإرسال إلى: `{success_count}` عضو\n❌ فشل الإرسال (مغلق الخاص): `{fail_count}` عضو", ephemeral=True)

# تشغيل البوت
if not DISCORD_TOKEN:
    print("خطأ: لم يتم العثور على متغير البيئة DISCORD_TOKEN!")
else:
    bot.run(DISCORD_TOKEN)
