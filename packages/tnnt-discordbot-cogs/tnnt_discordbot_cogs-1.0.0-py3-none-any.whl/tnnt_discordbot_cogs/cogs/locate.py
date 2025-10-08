"""
"Locator" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import logging

# Third Party
from corptools.models import EveItemType, MapSystem
from corptools.providers import esi
from discord import Colour, Embed, option
from discord.ext import commands
from pendulum.datetime import DateTime

# Django
from django.core.exceptions import ObjectDoesNotExist

# Alliance Auth
from allianceauth.eveonline.evelinks import dotlan, evewho
from allianceauth.eveonline.models import EveCharacter
from esi.models import Token

# Alliance Auth Discord Bot
from aadiscordbot.app_settings import get_all_servers
from aadiscordbot.cogs.utils.autocompletes import search_characters
from aadiscordbot.cogs.utils.decorators import message_in_channels, sender_has_perm

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog
from tnnt_discordbot_cogs.models.setting import Setting

logger = logging.getLogger(__name__)


class Locator(commands.Cog):
    """
    A cog to locate characters and their alts in EVE Online.
    """

    def __init__(self, bot):
        """
        Initializes the Locator cog.

        :param bot: The bot instance to which this cog is added.
        :type bot: discord.ext.commands.Bot
        """

        self.bot = bot

    @staticmethod
    def _get_locate_channels() -> list:
        """
        Get the locate channels from the settings.

        :return: List of locate channels or an empty list if none are set.
        :rtype: dict
        """

        locate_channels = Setting.get_setting(Setting.Field.LOCATE_CHANNELS.value).all()

        return (
            [channel.channel for channel in locate_channels if channel is not None]
            if locate_channels
            else []
        )

    @staticmethod
    def _get_locate_embeds(char: EveCharacter) -> list[Embed]:
        """
        Generates embeds for the character's alts' locations.

        :param char: The character for which to generate the embeds.
        :type char: allianceauth.eveonline.models.EveCharacter
        :return: A list of Discord embeds containing the location information of the character's alts.
        :rtype: list[discord.Embed]
        """

        def _process_alt_list(
            header: str, characters: list[dict], color: Colour = Colour.default()
        ) -> list[Embed]:
            """
            Processes a list of alt characters and generates embeds for them.

            :param header: The header for the embed.
            :type header: str
            :param characters: The list of characters to process.
            :type characters: list[dict]
            :param color: The color for the embed.
            :type color: discord.Colour
            :return: A list of Discord embeds containing the alt character information.
            :rtype: list[discord.Embed]
            """

            embeds = []

            # Process alts in chunks of 10
            for alt_grp in [
                characters[i : i + 10] for i in range(0, len(characters), 10)
            ]:
                altstr = []

                for a in alt_grp:
                    evewho_character = evewho.character_url(eve_id=a["cid"])
                    evewho_corporation = evewho.corporation_url(eve_id=a["crpid"])

                    character_line = f"[{a['cnm']}]({evewho_character}) [[{a['crpnm']}]({evewho_corporation})]"

                    if a["lookup"]:
                        dotlan_system = dotlan.solar_system_url(name=a["system_name"])
                        altstr.append(
                            f"### {character_line}\n"
                            f"**Current Location:** [{a['system_name']}]({dotlan_system})\n"
                            f"**Currently Flying:** {a['ship']}\n"
                            f"**Last Online:** {a['last_online'].strftime('%Y-%m-%d %H:%M')}\n"
                        )
                    else:
                        altstr.append(character_line + "\n")

                embed = Embed(title=header, description="\n".join(altstr), colour=color)
                embeds.append(embed)

            return embeds

        alts = char.character_ownership.user.character_ownerships.all().select_related(
            "character"
        )

        alt_online = []
        alt_offline = []
        alt_no_token = []

        for alt in alts:
            _alt = {
                "cid": alt.character.character_id,
                "cnm": alt.character.character_name,
                "crpid": alt.character.corporation_id,
                "crpnm": alt.character.corporation_name,
                "last_online": DateTime.min,
                "online": False,
                "ship": "",
                "system": None,
                "lookup": False,
            }
            scopes = [
                # Locations
                "esi-location.read_location.v1",
                "esi-location.read_online.v1",
                "esi-location.read_ship_type.v1",
            ]

            token = Token.get_token(
                character_id=alt.character.character_id, scopes=scopes
            )

            if token:
                try:
                    # Get all location data in one go
                    character_id = alt.character.character_id
                    valid_token = token.valid_access_token()

                    online = esi.client.Location.get_characters_character_id_online(
                        character_id=character_id,
                        token=valid_token,
                    ).result()

                    location = esi.client.Location.get_characters_character_id_location(
                        character_id=character_id,
                        token=valid_token,
                    ).result()

                    ship = esi.client.Location.get_characters_character_id_ship(
                        character_id=character_id,
                        token=valid_token,
                    ).result()

                    # Update alt data
                    _alt["online"] = (
                        "**Online**" if online.get("online", False) else "**Offline**"
                    )
                    _alt["last_online"] = online.get("last_logout", DateTime.min)

                    solar_system = MapSystem.objects.get(
                        system_id=location["solar_system_id"]
                    )
                    _alt["system_name"] = solar_system.name

                    current_ship, _ = EveItemType.objects.get_or_create_from_esi(
                        ship["ship_type_id"]
                    )
                    _alt["ship"] = current_ship
                    _alt["lookup"] = True

                    if online.get("online", False):
                        alt_online.append(_alt)
                    else:
                        alt_offline.append(_alt)

                except Exception as e:
                    logger.error(
                        f"Error fetching location data for character {alt.character.character_name}: {e}"
                    )
                    alt_no_token.append(_alt)
            else:
                alt_no_token.append(_alt)

        out_embeds = []

        # Process each category if it has items
        for header, alt_list, color in [
            ("Online Characters", alt_online, Colour.green()),
            ("Offline Characters", alt_offline, Colour.orange()),
            ("No Tokens", alt_no_token, Colour.red()),
        ]:
            if alt_list:
                out_embeds += _process_alt_list(
                    header=header, characters=alt_list, color=color
                )

        return out_embeds

    @message_in_channels(channels=_get_locate_channels())
    @sender_has_perm("tnnt_discordbot_cogs.locate")
    @commands.slash_command(name="locate", guild_ids=get_all_servers())
    @option(
        name="character",
        description="Search for a Character!",
        autocomplete=search_characters,
    )
    async def locate(self, ctx, character: str):
        """
        Slash command to locate a character and their alts in EVE Online.

        :param ctx:
        :type ctx:
        :param character:
        :type character:
        :return:
        :rtype:
        """

        try:
            char = EveCharacter.objects.get(character_name=character)
        except EveCharacter.DoesNotExist:
            return await ctx.respond(
                f"Character **{character}** does not exist in our Auth system",
                ephemeral=True,
            )

        try:
            main = char.character_ownership.user.profile.main_character
        except ObjectDoesNotExist:
            return await ctx.respond(
                f"Character **{character}** Unlinked in auth", ephemeral=True
            )

        try:
            discord_string = f"<@{char.character_ownership.user.discord.uid}>"
        except Exception as e:
            logger.error(e)
            discord_string = "unknown"

        await ctx.respond(
            (
                f"Looking up the location of all known alts of {main} ({discord_string})\n"
                "Please Wait..."
            ),
            ephemeral=True,
        )

        embeds = self._get_locate_embeds(char)

        for e in embeds:
            await ctx.respond(embed=e, ephemeral=True)


def setup(bot):
    # Unload the Members cog from `aadiscordbot`
    unload_cog(bot=bot, cog_name="Locator")

    # Add the Lookup cog to the bot
    bot.add_cog(Locator(bot))
