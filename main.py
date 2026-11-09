import os
import discord
from discord import app_commands
from discord.ext import commands

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    raise ValueError("خطأ: لم يتم العثور على متغير البيئة DISCORD_TOKEN.")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.moderation = True

bot = commands.Bot(command_prefix="!", intents=intents)

# تحديد آيدي سيرفرك حصرياً لتسجيل أوامر السلاش عليه
MY_GUILD_ID = discord.Object(id=1527790414751338731)

# ==========================================
# أنظمة الحماية الصارمة (Anti-Exploit & Security)
# ==========================================

@bot.event
async def on_member_join(member):
    if member.bot:
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
            if entry.target.id == member.id:
                adder = entry.user
                try:
                    await member.edit(roles=[], reason="حماية السيرفر: ممنوع دخول بوتات خارجية")
                except:
                    pass
                if adder and not adder.bot:
                    try:
                        guild_adder = member.guild.get_member(adder.id)
                        if guild_adder:
                            await guild_adder.edit(roles=[], reason="حماية السيرفر: قام بإضافة بوت خارجي")
                    except:
                        pass

@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        if entry.user and not entry.user.bot:
            user = channel.guild.get_member(entry.user.id)
            if user:
                try:
                    await user.edit(roles=[], reason="حماية السيرفر: قام بحذف روم")
                except:
                    pass
            break

@bot.event
async def on_member_update(before, after):
    if len(after.roles) > len(before.roles):
        async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == after.id and entry.user and not entry.user.bot:
                added_roles = [r for r in after.roles if r not in before.roles]
                if len(added_roles) > 3:
                    granter = after.guild.get_member(entry.user.id)
                    if granter:
                        try:
                            await granter.edit(roles=[], reason="حماية السيرفر: أعطى أكثر من 3 رولات دفعة واحدة")
                        except:
                            pass
                break


@bot.event
async def on_ready():
    try:
        bot.tree.copy_global_to(guild=MY_GUILD_ID)
        synced = await bot.tree.sync(guild=MY_GUILD_ID)
        print(f"Synced {len(synced)} slash commands to guild successfully.")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")
    print(f'Logged in as {bot.user} successfully, N7Z-Bot is online!')


def check_admin_or_streamer(interaction: discord.Interaction) -> bool:
    is_admin = interaction.user.guild_permissions.administrator
    has_streamer_role = any(role.name.lower() in ["streamer", "ستريمر"] for role in interaction.user.roles)
    return is_admin or has_streamer_role


# أمر البرودكاست في الخاص مع منشن في النهاية
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

bot.run(DISCORD_TOKEN)
