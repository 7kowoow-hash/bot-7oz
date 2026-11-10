import os
import discord
from discord.ext import commands

# 1. إعدادات البوت والصلاحيات (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # مهم جداً لجلب الأعضاء وإرسال الرسائل الخاصة لهم

bot = commands.Bot(command_prefix="!", intents=intents)

# أيدي السيرفر الخاص بك للمزامنة الفورية لأوامر السلاش
GUILD_ID = discord.Object(id=1527790414751338731)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user} (ID: {bot.user.id})")
    
    try:
        bot.tree.copy_global_to(guild=GUILD_ID)
        await bot.tree.sync(guild=GUILD_ID)
        print("تمت مزامنة أوامر السلاش (Slash Commands) مع السيرفر بنجاح!")
    except Exception as e:
        print(f"حدث خطأ أثناء مزامنة الأوامر: {e}")

# ==========================================
# أمثلة الأوامر وأمر البرودكاست (Broadcast)
# ==========================================

@bot.tree.command(name="ping", description="فحص سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 البوت شغال وسريع! البينغ: `{latency}ms`", ephemeral=True)

@bot.tree.command(name="broadcast", description="إرسال رسالة برودكاست عامة مع منشن وفي الخاص للأعضاء")
async def broadcast(interaction: discord.Interaction, message: str):
    # التحقق مما إذا كان المستخدم يملك صلاحية الأدمن أو الإدارة
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص للإداريين فقط!", ephemeral=True)
        return

    # الرد السريع لكي لا تنتهي مهلة التفاعل (Interaction)
    await interaction.response.send_message("⏳ جاري تنفيذ البرودكاست وإرسال الرسائل...", ephemeral=True)

    success_count = 0
    fail_count = 0

    # 1. إرسال الرسالة في الشات العام مع منشن لجميع الأعضاء في آخرها
    public_channel = interaction.channel
    if public_channel:
        # إضافة منشن لجميع الأعضاء أو استخدام @everyone
        public_text = f"{message}\n\n@everyone"
        await public_channel.send(public_text)

    # 2. إرسال الرسالة في الخاص (DM) لكل عضو في السيرفر
    for member in interaction.guild.members:
        if member.bot:
            continue  # تخطي البوتات
        try:
            await member.send(f"📬 **برودكاست إداري من سيرفر {interaction.guild.name}:**\n\n{message}")
            success_count += 1
        except Exception:
            fail_count += 1  # في حال كان العضو مقفل الخاص (DMs)

    # إرسال تقرير نهائي للإداري الذي نفذ الأمر
    try:
        await interaction.followup.send(
            f"✅ **تم الانتهاء من البرودكاست بنجاح!**\n"
            f"• تم الإرسال للعام مع المنشن.\n"
            f"• تم إرسالها بالخاص لـ **{success_count}** عضو.\n"
            f"• تعذر الإرسال لـ **{fail_count}** عضو (بسبب إغلاق الخاص).",
            ephemeral=True
        )
    except Exception:
        pass

# تشغيل البوت باستخدام التوكن من بيئة العمل (Railway Variables)
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("خطأ: لم يتم العثور على DISCORD_TOKEN في المتغيرات البيئية!")
else:
    bot.run(TOKEN)
