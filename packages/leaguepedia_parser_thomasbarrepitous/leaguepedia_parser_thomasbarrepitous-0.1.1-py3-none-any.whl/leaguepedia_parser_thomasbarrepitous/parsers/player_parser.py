import dataclasses
from typing import Optional, List
from leaguepedia_parser_thomasbarrepitous.site.leaguepedia import leaguepedia
import datetime
import enum

# Will rewrite this parser with Mixins or something more modular when I have more time.


class PlayerStatus(enum.Enum):
    ACTIVE = 0
    RETIRED = 1
    MOVED_TO_WILDRIFT = 2
    MOVED_TO_VALORANT = 3


@dataclasses.dataclass
class PlayerInfo:
    """Represents comprehensive player data from Leaguepedia's Players table.

    Attributes:
        id: Unique player identifier from Leaguepedia
        overview_page: The overview page of the player, useful for disambiguation
        player: The player's name
        image: The player's image
        name: The player's name
        native_name: The player's native name
        name_alphabet: The player's name in alphabet
        name_full: The player's full name
        country: The player's country
        nationality: The player's nationality
        nationality_primary: The player's primary nationality
        residency: The player's residency
        residency_former: The player's former residency
        age: The player's age
        birthdate: The player's birthdate
        deathdate: The player's deathdate
        team: The player's team
        team2: The player's second team
        current_teams: The player's current teams
        team_system: The player's team system
        team2_system: The player's second team system
        team_last: The player's last team
        role: The player's role
        role_last: The player's last role
        contract: The player's contract
        fav_champs: The player's favorite champions
        soloqueue_ids: The player's soloqueue ids
        askfm: The player's askfm
        bluesky: The player's bluesky
        discord: The player's discord
        facebook: The player's facebook
        instagram: The player's instagram
        lolpros: The player's lolpros
        reddit: The player's reddit
        snapchat: The player's snapchat
        stream: The player's stream
        twitter: The player's twitter
        threads: The player's threads
        linkedin: The player's linkedin
        vk: The player's vk
        website: The player's website
        weibo: The player's weibo
        youtube: The player's youtube
        is_retired: The player's retired status
        to_wildrift: The player's moved to wildrift status
        to_valorant: The player's moved to valorant status
        is_personality: The player's personality status
        is_substitute: The player's substitute status
        is_trainee: The player's trainee status
        is_lowercase: The player's lowercase status
        is_auto_team: The player's auto team status
        is_low_content: The player's low content status
    """

    # Identification fields
    id: Optional[str] = None
    overview_page: Optional[str] = None
    player: Optional[str] = None
    image: Optional[str] = None

    # Name fields
    name: Optional[str] = None
    native_name: Optional[str] = None
    name_alphabet: Optional[str] = None
    name_full: Optional[str] = None

    # Location fields
    country: Optional[str] = None
    nationality: List[str] = dataclasses.field(default_factory=list)
    nationality_primary: Optional[str] = None
    residency: Optional[str] = None
    residency_former: Optional[str] = None

    # Demographic fields
    age: Optional[int] = None
    birthdate: Optional[datetime.date] = None
    deathdate: Optional[datetime.date] = None

    # Team fields
    team: Optional[str] = None
    team2: Optional[str] = None
    current_teams: List[str] = dataclasses.field(default_factory=list)
    team_system: Optional[str] = None
    team2_system: Optional[str] = None
    team_last: Optional[str] = None

    # Role fields
    role: Optional[str] = None
    role_last: List[str] = dataclasses.field(default_factory=list)

    # Contract dates
    contract: Optional[datetime.date] = None

    # Game data
    fav_champs: List[str] = dataclasses.field(default_factory=list)
    soloqueue_ids: Optional[str] = None

    # Social media & profiles
    askfm: Optional[str] = None
    bluesky: Optional[str] = None
    discord: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    lolpros: Optional[str] = None
    reddit: Optional[str] = None
    snapchat: Optional[str] = None
    stream: Optional[str] = None
    twitter: Optional[str] = None
    threads: Optional[str] = None
    linkedin: Optional[str] = None
    vk: Optional[str] = None
    website: Optional[str] = None
    weibo: Optional[str] = None
    youtube: Optional[str] = None

    # Status flags
    is_retired: Optional[bool] = None
    to_wildrift: Optional[bool] = None
    to_valorant: Optional[bool] = None
    is_personality: Optional[bool] = None
    is_substitute: Optional[bool] = None
    is_trainee: Optional[bool] = None
    is_lowercase: Optional[bool] = None
    is_auto_team: Optional[bool] = None
    is_low_content: Optional[bool] = None

    @property
    def status(self) -> PlayerStatus:
        if self.to_wildrift:
            return PlayerStatus.MOVED_TO_WILDRIFT
        if self.to_valorant:
            return PlayerStatus.MOVED_TO_VALORANT
        return PlayerStatus.ACTIVE


def is_active(player: PlayerInfo) -> bool:
    return not any([player.is_retired, player.to_wildrift, player.to_valorant])


def _parse_player_data(data: dict) -> PlayerInfo:
    """Parses raw API response data into a complete PlayerInfo object."""

    # Date parsing helper
    def parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
        try:
            return (
                datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_str
                else None
            )
        except ValueError:
            return None

    # List parsing helper
    def parse_list(field: Optional[str], delimiter: str = ",") -> List[str]:
        if not field:
            return []
        return [item.strip() for item in field.split(delimiter) if item.strip()]

    # Handle special boolean fields
    def parse_bool(field: Optional[str]) -> Optional[bool]:
        return field == "Yes" if field else None

    # Simplified to always get the field from data
    def get_field(field_name: str, default=None):
        return data.get(field_name, default)

    return PlayerInfo(
        # Identification
        id=get_field("ID"),
        overview_page=get_field("OverviewPage"),
        player=get_field("Player"),
        image=get_field("Image"),
        # Names
        name=get_field("Name"),
        native_name=get_field("NativeName"),
        name_alphabet=get_field("NameAlphabet"),
        name_full=get_field("NameFull"),
        # Location
        country=get_field("Country"),
        nationality=parse_list(get_field("Nationality")),
        nationality_primary=get_field("NationalityPrimary"),
        residency=get_field("Residency"),
        residency_former=get_field("ResidencyFormer"),
        # Demographics
        age=int(get_field("Age"))
        if get_field("Age") and get_field("Age").isdigit()
        else None,
        birthdate=parse_date(get_field("Birthdate")),
        deathdate=parse_date(get_field("Deathdate")),
        # Teams
        team=get_field("Team"),
        team2=get_field("Team2"),
        current_teams=parse_list(get_field("CurrentTeams")),
        team_system=get_field("TeamSystem"),
        team2_system=get_field("Team2System"),
        team_last=get_field("TeamLast"),
        # Roles
        role=get_field("Role"),
        role_last=parse_list(get_field("RoleLast"), ";"),
        # Contract
        contract=parse_date(get_field("Contract")),
        # Game Data
        fav_champs=parse_list(get_field("FavChamps")),
        soloqueue_ids=get_field("SoloqueueIds"),
        # Social Media
        askfm=get_field("Askfm"),
        bluesky=get_field("Bluesky"),
        discord=get_field("Discord"),
        facebook=get_field("Facebook"),
        instagram=get_field("Instagram"),
        lolpros=get_field("Lolpros"),
        reddit=get_field("Reddit"),
        snapchat=get_field("Snapchat"),
        stream=get_field("Stream"),
        twitter=get_field("Twitter"),
        threads=get_field("Threads"),
        linkedin=get_field("LinkedIn"),
        vk=get_field("Vk"),
        website=get_field("Website"),
        weibo=get_field("Weibo"),
        youtube=get_field("Youtube"),
        # Status Flags
        is_retired=parse_bool(get_field("IsRetired")),
        to_wildrift=parse_bool(get_field("ToWildrift")),
        to_valorant=parse_bool(get_field("ToValorant")),
        is_personality=parse_bool(get_field("IsPersonality")),
        is_substitute=parse_bool(get_field("IsSubstitute")),
        is_trainee=parse_bool(get_field("IsTrainee")),
        is_lowercase=parse_bool(get_field("IsLowercase")),
        is_auto_team=parse_bool(get_field("IsAutoTeam")),
        is_low_content=parse_bool(get_field("IsLowContent")),
    )


def get_player_by_name(player_name: str) -> PlayerInfo:
    """
    Retrieves comprehensive player information from Leaguepedia's Players table.
    https://lol.fandom.com/wiki/Special:CargoTables/Players

    Args:
        player_name (str): Exact player name as stored in Leaguepedia's 'Player' field

    Returns:
        PlayerInfo: Dataclass containing all available player information

    Raises:
        ValueError: If player is not found
        RuntimeError: If there's an error querying Leaguepedia
    """
    try:
        # Always query all fields
        query_fields = ",".join(f"P.{f}" for f in _FULL_QUERY_FIELDS)

        query = leaguepedia.query(
            tables="Players=P",
            fields=query_fields,
            where=f"P.Player = '{player_name}'",
        )

        if not query:
            raise ValueError(
                f"Player '{player_name}' not found in Leaguepedia database"
            )

        # Parse all fields without filtering
        return _parse_player_data(query[0])

    except Exception as e:
        raise RuntimeError(f"Failed to fetch player data for {player_name}: {str(e)}")


# Complete list of valid fields from Cargo table
_FULL_QUERY_FIELDS = [
    "ID",
    "OverviewPage",
    "Player",
    "Image",
    "Name",
    "NativeName",
    "NameAlphabet",
    "NameFull",
    "Country",
    "Nationality",
    "NationalityPrimary",
    "Residency",
    "ResidencyFormer",
    "Age",
    "Birthdate",
    "Deathdate",
    "Team",
    "Team2",
    "CurrentTeams",
    "TeamSystem",
    "Team2System",
    "TeamLast",
    "Role",
    "RoleLast",
    "Contract",
    "FavChamps",
    "SoloqueueIds",
    "Askfm",
    "Bluesky",
    "Discord",
    "Facebook",
    "Instagram",
    "Lolpros",
    "Reddit",
    "Snapchat",
    "Stream",
    "Twitter",
    "Threads",
    "LinkedIn",
    "Vk",
    "Website",
    "Weibo",
    "Youtube",
    "IsRetired",
    "ToWildrift",
    "ToValorant",
    "IsPersonality",
    "IsSubstitute",
    "IsTrainee",
    "IsLowercase",
    "IsAutoTeam",
    "IsLowContent",
]
