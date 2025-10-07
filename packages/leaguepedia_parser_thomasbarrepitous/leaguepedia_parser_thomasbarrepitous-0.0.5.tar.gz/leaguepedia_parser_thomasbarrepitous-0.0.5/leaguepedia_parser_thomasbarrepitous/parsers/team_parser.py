import dataclasses
from typing import Optional, List, Set
from leaguepedia_parser_thomasbarrepitous.site.leaguepedia import leaguepedia

VALID_ROLES: Set[str] = {"Top", "Jungle", "Mid", "Bot", "Support"}


@dataclasses.dataclass
class TeamAssets:
    thumbnail_url: str
    logo_url: str
    long_name: str  # Aka display name


@dataclasses.dataclass
class TeamPlayer:
    name: str
    role: str


def _clean_player_name(player_name: str) -> str:
    """
    Extracts the player's in-game name when it's followed by their real name in parentheses.
    Ex: "Doran (Choi Hyeon-joon)" -> "Doran"
    But "Naak Nako" remains "Naak Nako"

    Args:
        player_name (str): The player's name, potentially including their real name in parentheses

    Returns:
        str: The cleaned player name
    """
    if not player_name:
        return ""

    # If there's a space followed by an opening parenthesis, take everything before it
    if " (" in player_name:
        return player_name.split(" (")[0]

    return player_name


def get_active_players(team_name: str, **kwargs) -> List[TeamPlayer]:
    """
    Retrieves the active players for a given team from Leaguepedia.

    This function queries Leaguepedia for players who have joined the team but haven't left yet.
    It processes roles for each player and returns a list of currently active players in the main roles
    (Top, Jungle, Mid, Bot, Support).

    Args:
        team_name (str): The name of the team to query active players for.
        date (str): The date to query active players for. (Optional)

    Returns:
        List[TeamPlayer]: A list of TeamPlayer objects representing the current active roster.

    Raises:
        ValueError: If the team_name is empty or None
        RuntimeError: If the Leaguepedia query fails
    """
    if not team_name:
        raise ValueError("Team name cannot be empty")

    active_players: List[TeamPlayer] = []
    date = kwargs.get("date")

    try:
        # Base where clause
        where_clause = f"T.Team = '{team_name}'"

        # Handle date filtering
        if date:
            where_clause += f" AND T.DateJoin <= '{date}' AND (T.DateLeave IS NULL OR T.DateLeave > '{date}')"
        else:
            where_clause += " AND T.DateLeave IS NULL"

        # Query active players with optional date filter
        query = leaguepedia.query(
            tables="Tenures=T, RosterChanges=RC",
            fields="T.Player, T.Team, T.DateJoin, RC.Roles",
            where=where_clause,
            join_on="T.RosterChangeIdJoin=RC.RosterChangeId",
            group_by="T.Player",
        )

        if not query:
            return []

        # Process each player's roles
        for player_data in query:
            primary_role = _get_primary_valid_role(player_data.get("Roles", ""))
            if primary_role:
                cleaned_name = _clean_player_name(player_data["Player"])
                player = TeamPlayer(name=cleaned_name, role=primary_role)
                active_players.append(player)

        return active_players

    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch active players for team {team_name}: {str(e)}"
        )


def _get_primary_valid_role(roles_str: str) -> Optional[str]:
    """
    Extract the primary valid role from a semicolon-separated string of roles.
    Ex: "Top;Jungle" -> "Top"
    In the case of Faker for example, his roles are "Mid;Part-Owner" and we only want to return "Mid".

    Args:
        roles_str (str): Semicolon-separated string of roles

    Returns:
        Optional[str]: The first valid role found, or None if no valid roles
    """
    if not roles_str:
        return None

    # Split roles and clean whitespace
    roles = [role.strip() for role in roles_str.split(";")]

    # Return the first role that matches our valid roles
    for role in roles:
        if role in VALID_ROLES:
            return role

    return None


def get_all_team_assets(team_link: str) -> TeamAssets:
    """

    Args:
        team_link: a field coming from Team1/Team2 in ScoreboardGames

    Returns:
        A TeamAssets object

    """
    result = leaguepedia.site.client.api(
        action="query",
        format="json",
        prop="imageinfo",
        titles=f"File:{team_link}logo square.png|File:{team_link}logo std.png",
        iiprop="url",
    )

    pages = result["query"]["pages"]

    urls = []
    for v in pages.values():
        urls.append(v["imageinfo"][0]["url"])

    long_name = leaguepedia.site.cache.get("Team", team_link, "link")

    return TeamAssets(
        thumbnail_url=urls[1],
        logo_url=urls[0],
        long_name=long_name,
    )


def get_team_logo(team_name: str, _retry=True) -> str:
    """
    Returns the team logo URL

    Params:
        team_name: Team name, usually gotten from the game dictionary
        _retry: whether or not to get the team's full name from Leaguepedia if it was not understood

    Returns:
        URL pointing to the team's logo
    """
    return _get_team_asset(f"File:{team_name}logo square.png", team_name, _retry)


def get_team_thumbnail(team_name: str, _retry=True) -> str:
    """
    Returns the team thumbnail URL

    Params:
        team_name: Team name, usually gotten from the game dictionary
        _retry: whether or not to get the team's full name from Leaguepedia if it was not understood

    Returns:
        URL pointing to the team's thumbnail
    """
    return _get_team_asset(f"File:{team_name}logo std.png", team_name, _retry)


def _get_team_asset(asset_name: str, team_name: str, _retry=True) -> str:
    """
    Returns the team thumbnail URL

    Params:
        team_name: Team name, usually gotten from the game dictionary
        _retry: whether or not to get the team's full name from Leaguepedia if it was not understood

    Returns:
        URL pointing to the team's logo
    """
    result = leaguepedia.site.client.api(
        action="query",
        format="json",
        prop="imageinfo",
        titles=asset_name,
        iiprop="url",
    )

    try:
        url = None
        pages = result.get("query", {}).get("pages", {})
        for k, v in pages.items():
            imageinfo = v.get("imageinfo")
            if imageinfo and len(imageinfo) > 0:
                url = imageinfo[0].get("url")
                break

    except (TypeError, AttributeError, IndexError, KeyError) as e:
        # This happens when the team name was not properly understood.
        if _retry:
            # Prevent infinite recursion by checking if we're already using the long name
            long_name = get_long_team_name_from_trigram(team_name)
            if long_name and long_name != team_name:
                return _get_team_asset(
                    asset_name.replace(team_name, long_name), long_name, False
                )
            else:
                raise ValueError(
                    f"Unable to resolve team name '{team_name}' to a valid team"
                )
        else:
            raise ValueError(f"Logo not found for team '{team_name}': {str(e)}")

    return url


def get_long_team_name_from_trigram(
    team_abbreviation: str,
    event_overview_page: str = None,
) -> Optional[str]:
    """
    Returns the long team name for the given team abbreviation using Leaguepedia's search pages

    Only issues a query the first time it is called, then stores the data in a cache
    There is no cache timeout at the moment

    Args:
        team_abbreviation: A team name abbreviation, like IG or RNG
        event_overview_page: The overviewPage field of the tournament, useful for disambiguation

    Returns:
        The long team name, like "Invictus Gaming" or "Royal Never Give Up"
    """

    # We use only lowercase team abbreviations for simplicity
    team_abbreviation = team_abbreviation.lower()

    if event_overview_page:
        return leaguepedia.site.cache.get_team_from_event_tricode(
            event_overview_page, team_abbreviation
        )

    else:
        return leaguepedia.site.cache.get("Team", team_abbreviation, "link")
