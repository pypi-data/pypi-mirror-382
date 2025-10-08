"""
"Lookup" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import csv
import io
import logging
from collections.abc import Coroutine
from typing import Any

# Third Party
from discord import (
    Color,
    Embed,
    File,
    Interaction,
    SlashCommandGroup,
    WebhookMessage,
    option,
)
from discord.ext import commands

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify

# Alliance Auth
from allianceauth.eveonline.evelinks import evewho
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

# Alliance Auth Discord Bot
from aadiscordbot import app_settings
from aadiscordbot.app_settings import aastatistics_active
from aadiscordbot.cogs.utils.autocompletes import (
    search_characters,
    search_corporations_on_characters,
)
from aadiscordbot.cogs.utils.decorators import (
    is_guild_managed,
    message_in_channels,
    sender_has_perm,
)

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog
from tnnt_discordbot_cogs.models.setting import Setting

logger = logging.getLogger(__name__)


class Lookup(commands.Cog):
    """
    All about users!
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the Lookup cog.

        :param bot: The bot instance to which this cog is attached.
        :type bot: commands.Bot
        """

        self.bot = bot

    lookup_commands = SlashCommandGroup(
        name="lookup",
        description="Server Admin Commands",
        guild_ids=app_settings.get_all_servers(),
    )

    @staticmethod
    def _get_lookup_channels() -> list:
        """
        Get the lookup channels from the settings.

        :return: List of lookup channels or an empty list if none are set.
        :rtype: list
        """

        lookup_channels = Setting.get_setting(
            setting_key=Setting.Field.LOOKUP_CHANNELS.value
        ).all()

        return (
            [channel.channel for channel in lookup_channels if channel is not None]
            if lookup_channels
            else []
        )

    @staticmethod
    def get_csv(character_name: str) -> File:
        """
        Generates a CSV file of all known alts for a given character name.

        :param character_name: The name of the character to look up.
        :type character_name: str
        :return: A CSV file containing the character's alts.
        :rtype: File
        """

        csv_file_basename = slugify(f"{character_name} known alts")
        char = EveCharacter.objects.get(character_name=character_name)
        alts = char.character_ownership.user.character_ownerships.all().select_related(
            "character"
        )
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        header = [
            "Character ID",
            "Character Name",
            "Corporation ID",
            "Corporation Name",
            "Alliance ID",
            "Alliance Name",
        ]
        writer.writerow(header)

        for a in alts:
            writer.writerow(
                [
                    a.character.character_id,
                    a.character.character_name,
                    a.character.corporation_id,
                    a.character.corporation_name,
                    a.character.alliance_id,
                    a.character.alliance_name,
                ]
            )

        buffer.seek(0)

        return File(fp=buffer, filename=f"{csv_file_basename}.csv")

    @staticmethod
    def get_lookup_embed(character_name: str) -> Embed:
        """
        Generates an embed with information about a character.

        :param character_name: The name of the character to look up.
        :type character_name: str
        :return: An embed containing the character's information, including linked characters, groups, and statistics.
        :rtype: Embed
        """

        embed = Embed(title=f"Character Lookup: {character_name}")

        try:
            char = EveCharacter.objects.get(character_name=character_name)

            try:
                main = char.character_ownership.user.profile.main_character
                state = char.character_ownership.user.profile.state.name
                groups = char.character_ownership.user.groups.all().values_list(
                    "name", flat=True
                )

                try:
                    discord_string = f"<@{char.character_ownership.user.discord.uid}>"
                except Exception as e:
                    logger.error(e)

                    discord_string = "unknown"

                if aastatistics_active():
                    alts = (
                        char.character_ownership.user.character_ownerships.all()
                        .select_related("character", "character_stats")
                        .values_list(
                            "character__character_name",
                            "character__corporation_ticker",
                            "character__character_id",
                            "character__corporation_id",
                            "character__character_stats__zk_12m",
                            "character__character_stats__zk_3m",
                            "character__character_stats__ships_destroyed",
                            "character__character_stats__ships_lost",
                            "character__character_stats__isk_destroyed",
                            "character__character_stats__isk_lost",
                        )
                    )
                    zk12 = 0
                    zk3 = 0
                    zk_ships_destroyed = 0
                    zk_ships_lost = 0
                    zk_isk_destroyed = 0
                    zk_isk_lost = 0
                else:
                    alts = (
                        char.character_ownership.user.character_ownerships.all()
                        .select_related("character")
                        .values_list(
                            "character__character_name",
                            "character__corporation_ticker",
                            "character__character_id",
                            "character__corporation_id",
                        )
                    )
                    zk12 = "Not Installed"
                    zk3 = "Not Installed"
                    zk_ships_destroyed = "Not Installed"
                    zk_ships_lost = "Not Installed"
                    zk_isk_destroyed = "Not Installed"
                    zk_isk_lost = "Not Installed"

                if aastatistics_active():
                    for alt in alts:
                        if alt[4]:
                            zk12 += alt[4]
                            zk3 += alt[5]

                        if alt[6]:
                            zk_ships_destroyed += alt[6]
                            zk_ships_lost += alt[7]
                            zk_isk_destroyed += alt[8]
                            zk_isk_lost += alt[9]

                embed.colour = Color.blue()
                embed.description = f"**{char}** is linked to **{main} [{main.corporation_ticker}]** (State: {state})"

                alt_list = [
                    f"[{a[0]}]({evewho.character_url(a[2])}) [[{a[1]}]({evewho.corporation_url(a[3])})]"
                    for a in alts
                ]

                for idx, names in enumerate(
                    [alt_list[i : i + 6] for i in range(0, len(alt_list), 6)]
                ):
                    if idx < 6:
                        embed.add_field(
                            name=f"Linked Characters {idx + 1}",
                            value="\n".join(names),
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=f"Linked Characters {idx} **(Discord Limited. There are More)**",
                            value="\n".join(names),
                            inline=False,
                        )
                        break

                if len(groups) > 0:
                    embed.add_field(
                        name="Groups", value="\n".join(groups), inline=False
                    )

                if aastatistics_active():
                    embed.add_field(
                        name="Recent zKillboard Statistics", value="", inline=False
                    )
                    embed.add_field(
                        name="Kills (last 12 months)",
                        value=f"{zk12:,}",
                        inline=True,
                    )
                    embed.add_field(
                        name="Kills (last 3 months)",
                        value=f"{zk3:,}",
                        inline=True,
                    )

                    embed.add_field(
                        name="Total Ship Destroyed/Lost", value="", inline=False
                    )
                    embed.add_field(
                        name="Ships Destroyed",
                        value=f"{zk_ships_destroyed:,}",
                        inline=True,
                    )
                    embed.add_field(
                        name="Ships Lost",
                        value=f"{zk_ships_lost:,}",
                        inline=True,
                    )

                    embed.add_field(
                        name="Total ISK Destroyed/Lost", value="", inline=False
                    )
                    embed.add_field(
                        name="ISK Destroyed",
                        value=f"{zk_isk_destroyed:,}",
                        inline=True,
                    )
                    embed.add_field(
                        name="ISK Lost", value=f"{zk_isk_lost:,}", inline=True
                    )

                embed.add_field(name="Discord Link", value=discord_string, inline=False)

                return embed
            except ObjectDoesNotExist:
                users = char.ownership_records.values("user")
                users = User.objects.filter(id__in=users)
                characters = EveCharacter.objects.filter(
                    ownership_records__user__in=users
                ).distinct()
                embed = Embed(title="Character Lookup")
                embed.colour = Color.blue()

                embed.description = f"**{char}** is unlinked. Searching for any characters linked to known users"
                user_names = [f"{user.username}" for user in users]

                if len(user_names) == 0:
                    user_names = "No user links found"
                else:
                    user_names = ", ".join(user_names)

                embed.add_field(name="Old Users", value=user_names, inline=False)

                alt_list = [
                    (
                        f"[{a.character_name}]({evewho.character_url(a.character_id)}) "
                        f"*[[{a.corporation_ticker}]({evewho.corporation_url(a.corporation_id)})]*"
                    )
                    for a in characters
                ]

                for idx, names in enumerate(
                    [alt_list[i : i + 6] for i in range(0, len(alt_list), 6)]
                ):
                    if idx < 6:
                        embed.add_field(
                            name=f"Found Characters {idx + 1}",
                            value=", ".join(names),
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=f"Found Characters {idx} **(Discord Limited. There are More)**",
                            value=", ".join(names),
                            inline=False,
                        )
                        break

                return embed
        except EveCharacter.DoesNotExist:
            embed.colour = Color.red()

            embed.description = (
                f"Character **{character_name}** does not exist in our Auth system"
            )

            return embed

    @staticmethod
    def build_corporation_embeds(corporation_name: str) -> list[Any] | None:
        """
        Builds embeds for a corporation based on the input name, showing all known alts in that corporation.

        :param corporation_name: The name of the corporation to look up.
        :type corporation_name: str
        :return: A list of embeds containing information about the corporation and its members, or None if no members are found.
        :rtype: list[Any] | None
        """

        chars = EveCharacter.objects.filter(corporation_name=corporation_name)

        if chars.count():
            corp_id = 0
            own_ids = [settings.DISCORD_BOT_MEMBER_ALLIANCES]
            alts_in_corp = []
            knowns = 0

            for c in chars:
                corp_id = c.corporation_id

                if c.alliance_id not in own_ids:
                    alts_in_corp.append(c)

            mains = {}

            for a in alts_in_corp:
                try:
                    main = a.character_ownership.user.profile.main_character

                    if main.character_id not in mains:
                        mains[main.character_id] = [main, 0]

                    mains[main.character_id][1] += 1
                    knowns += 1
                except Exception:
                    # logger.error(e)
                    pass

            output = []
            base_string = "[{}]({}) [[{}]({})] has {} character{}"

            for k, m in mains.items():
                output.append(
                    base_string.format(
                        m[0],
                        evewho.character_url(m[0].character_id),
                        m[0].corporation_ticker,
                        evewho.corporation_url(m[0].corporation_id),
                        m[1],
                        "s" if m[1] > 1 else "",
                    )
                )
            embeds = []

            corp_info = EveCorporationInfo.provider.get_corporation(corp_id)

            msg = (
                f"**[[{corp_info.ticker}]({evewho.corporation_url(corp_id)})]** has {corp_info.members} members:\n\n"
                "```diff\n"
                f"+Known Members     : {knowns}\n"
                f"-Unknowns          : {corp_info.members - knowns}```"
            )

            _header = Embed(title=corporation_name, description=msg)

            embeds.append(_header)

            for strings in [output[i : i + 10] for i in range(0, len(output), 10)]:
                embed = Embed(title=corporation_name)
                embed.colour = Color.blue()
                embed.description = "\n".join(strings)
                embeds.append(embed)

            return embeds

        return None

    @lookup_commands.command(
        name="character",
        description="Looks up a character in the Auth system and returns information about them.",
        guild_ids=app_settings.get_all_servers(),
    )
    @is_guild_managed()
    @sender_has_perm(perm="tnnt_discordbot_cogs.lookup")
    @message_in_channels(channels=_get_lookup_channels())
    @option(
        name="character",
        description="Search for a character",
        autocomplete=search_characters,
    )
    @option(name="gib_csv", description="Output a CSV of all characters")
    async def slash_lookup_character(
        self, ctx, character: str, gib_csv: bool = False
    ) -> Coroutine[Any, Any, Interaction | WebhookMessage]:
        """
        Looks up a character in the Auth system and returns information about them.
        Input: a Eve Character Name
        Example: `/lookup character: John Doe gib_csv: True`

        :param ctx: Discord context for the command.
        :type ctx:
        :param character: The name of the character to look up.
        :type character: str
        :param gib_csv: Whether to output a CSV of all characters linked to the character.
        :type gib_csv: bool
        :return: An interaction response with the character's information or a CSV file if requested.
        :rtype: Coroutine[Any, Any, Interaction | WebhookMessage]
        """

        await ctx.defer(ephemeral=True)

        if gib_csv:
            file = self.get_csv(character)

            return await ctx.respond(
                embed=self.get_lookup_embed(character), file=file, ephemeral=True
            )

        return await ctx.respond(embed=self.get_lookup_embed(character), ephemeral=True)

    @lookup_commands.command(
        name="corporation",
        description="Looks up a corporation and returns information about its members.",
        guild_ids=app_settings.get_all_servers(),
    )
    @is_guild_managed()
    @sender_has_perm(perm="tnnt_discordbot_cogs.lookup")
    @message_in_channels(channels=_get_lookup_channels())
    @option(
        name="corporation",
        description="Search for a corporation",
        autocomplete=search_corporations_on_characters,
    )
    async def slash_lookup_corporation(
        self, ctx, corporation: str
    ) -> Coroutine[Any, Any, Interaction | WebhookMessage] or None:
        """
        Gets Auth data about a given corporation.

        :param ctx: Discord context for the command.
        :type ctx:
        :param corporation: The name of the corporation to look up.
        :type corporation: str
        :return: An interaction response with the corporation's information or a message indicating no members found.
        :rtype: Coroutine[Any, Any, Interaction | WebhookMessage] or None
        """

        await ctx.defer(ephemeral=True)

        embeds = self.build_corporation_embeds(corporation_name=corporation)

        if len(embeds):
            e = embeds.pop(0)

            await ctx.respond(embed=e, ephemeral=True)

            for e in embeds:
                await ctx.respond(embed=e, ephemeral=True)

            return None
        else:
            return await ctx.respond("No Members Found!", ephemeral=True)


def setup(bot: commands.Bot) -> None:
    """
    Setup function for the Lookup cog.

    :param bot: The bot instance to which this cog is attached.
    :type bot: commands.Bot
    :return: None
    :rtype: None
    """

    # Unload any other Lookup cog
    unload_cog(bot=bot, cog_name="Lookup")

    # Unload the Members cog from `aadiscordbot`
    unload_cog(bot=bot, cog_name="Members")

    # Add the Lookup cog to the bot
    bot.add_cog(Lookup(bot))
