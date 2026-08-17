import discord
from discord import app_commands
from discord.ext import commands

# ==================== НАСТРОЙКИ ====================
TOKEN = "MTUzODkxODAwMjkyMDI2NzkyOA.Gxa0C4.1i6EKs7FBFGPc7QQlKsIKWfWriy-HUQP0t-xzM"

GUILD_ID = 1538576529506836500          # ID вашего сервера
LEADER_ROLE_ID = 1538583737132916847    # ID роли "Лидер"
TICKET_CATEGORY_ID = 1538578924299358258    # ID категории, куда будут падать тикеты
# =====================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def is_staff(member: discord.Member) -> bool:
    """Проверка: лидер или админ."""
    role_ids = {r.id for r in member.roles}
    return LEADER_ROLE_ID in role_ids or ADMIN_ROLE_ID in role_ids or member.guild_permissions.administrator


class CloseTicketView(discord.ui.View):
    """Кнопка закрытия тикета (доступна только лидеру/админу)."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Закрыть тикет", style=discord.ButtonStyle.danger, custom_id="close_ticket_button")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user

        if not is_staff(member):
            await interaction.response.send_message(
                "❌ Закрыть тикет может только лидер или администратор.", ephemeral=True
            )
            return

        await interaction.response.send_message("Тикет будет закрыт через 5 секунд...")
        await interaction.channel.send(f"Тикет закрыт пользователем {member.mention}.")
        await discord.utils.sleep_until(discord.utils.utcnow() + __import__("datetime").timedelta(seconds=5))
        await interaction.channel.delete()


class OpenTicketView(discord.ui.View):
    """Кнопка создания тикета — можно повесить в отдельном канале."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Создать тикет", style=discord.ButtonStyle.success, custom_id="open_ticket_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        author = interaction.user

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{author.name.lower()}")
        if existing:
            await interaction.response.send_message(
                f"У вас уже есть открытый тикет: {existing.mention}", ephemeral=True
            )
            return

        category = guild.get_channel(TICKET_CATEGORY_ID)
        leader_role = guild.get_role(LEADER_ROLE_ID)
        admin_role = guild.get_role(ADMIN_ROLE_ID)

        # Права: видит только автор + лидер/админ. Остальным всё запрещено.
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            author: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, manage_channels=True
            ),
        }
        if leader_role:
            overwrites[leader_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True, manage_channels=True
            )
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True, manage_channels=True
            )

        channel = await guild.create_text_channel(
            name=f"ticket-{author.name.lower()}",
            category=category,
            overwrites=overwrites,
            topic=f"Тикет пользователя {author.id}",
        )

        embed = discord.Embed(
            title="Тикет создан",
            description=(
                f"Здравствуйте, {author.mention}!\n"
                "Опишите свою проблему, и лидер или администратор скоро вам ответит.\n\n"
                "Закрыть тикет может только лидер или администратор."
            ),
            color=discord.Color.blurple(),
        )

        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"Ваш тикет создан: {channel.mention}", ephemeral=True)


@bot.event
async def on_ready():
    # Регистрируем "вечные" View, чтобы кнопки работали после перезапуска бота
    bot.add_view(OpenTicketView())
    bot.add_view(CloseTicketView())

    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Бот запущен как {bot.user}")


@bot.tree.command(name="ticket_panel", description="Отправить панель для создания тикетов", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Поддержка",
        description="Нажмите на кнопку ниже, чтобы создать тикет.",
        color=discord.Color.green(),
    )
    await interaction.channel.send(embed=embed, view=OpenTicketView())
    await interaction.response.send_message("Панель отправлена.", ephemeral=True)


bot.run(TOKEN)
