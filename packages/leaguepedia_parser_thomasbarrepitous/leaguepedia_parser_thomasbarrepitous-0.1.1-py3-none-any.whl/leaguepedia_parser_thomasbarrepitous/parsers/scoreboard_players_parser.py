import dataclasses
from typing import List, Optional
from datetime import datetime

from leaguepedia_parser_thomasbarrepitous.site.leaguepedia import leaguepedia
from leaguepedia_parser_thomasbarrepitous.transmuters.field_names import (
    scoreboard_players_fields,
)


@dataclasses.dataclass
class ScoreboardPlayer:
    """Represents a player's performance statistics from a single game.

    Attributes:
        overview_page: Tournament overview page (String)
        name: Player name (String)
        link: Player identifier with disambiguation (String)
        champion: Champion played (String)
        kills: Player eliminations (Integer)
        deaths: Times player was eliminated (Integer)
        assists: Player kill participation (Integer)
        summoner_spells: Summoner spells used (List of String)
        gold: Total gold earned (Integer)
        cs: Creep score - minions and monsters killed (Integer)
        damage_to_champions: Damage dealt to enemy champions (Integer)
        vision_score: Vision score metric (Integer)
        items: Items purchased (List of String)
        trinket: Trinket used (String)
        keystone_mastery: Keystone mastery if applicable (String)
        keystone_rune: Keystone rune if applicable (String)
        primary_tree: Primary rune tree (String)
        secondary_tree: Secondary rune tree (String)
        runes: Complete rune information (String)
        team_kills: Total team kills (Integer)
        team_gold: Total team gold (Integer)
        team: Team name (String)
        team_vs: Opposing team (String)
        time: Game time (Datetime)
        player_win: Whether player won (String)
        datetime_utc: Game datetime in UTC (Datetime)
        dst: Daylight savings indicator (String)
        tournament: Tournament name (String)
        role: Player role (String)
        role_number: Role number (Integer)
        ingame_role: In-game role (String)
        side: Side of the map (Integer)
        unique_line: Unique line identifier (String)
        unique_line_vs: Opposing unique line (String)
        unique_role: Unique role identifier (String)
        unique_role_vs: Opposing unique role (String)
        game_id: Game identifier (String)
        match_id: Match identifier (String)
        game_team_id: Game team identifier (String)
        game_role_id: Game role identifier (String)
        game_role_id_vs: Opposing game role identifier (String)
        stats_page: Statistics page reference (String)
    """

    overview_page: Optional[str] = None
    name: Optional[str] = None
    link: Optional[str] = None
    champion: Optional[str] = None
    kills: Optional[int] = None
    deaths: Optional[int] = None
    assists: Optional[int] = None
    summoner_spells: Optional[List[str]] = None
    gold: Optional[int] = None
    cs: Optional[int] = None
    damage_to_champions: Optional[int] = None
    vision_score: Optional[int] = None
    items: Optional[List[str]] = None
    trinket: Optional[str] = None
    keystone_mastery: Optional[str] = None
    keystone_rune: Optional[str] = None
    primary_tree: Optional[str] = None
    secondary_tree: Optional[str] = None
    runes: Optional[str] = None
    team_kills: Optional[int] = None
    team_gold: Optional[int] = None
    team: Optional[str] = None
    team_vs: Optional[str] = None
    time: Optional[datetime] = None
    player_win: Optional[str] = None
    datetime_utc: Optional[datetime] = None
    dst: Optional[str] = None
    tournament: Optional[str] = None
    role: Optional[str] = None
    role_number: Optional[int] = None
    ingame_role: Optional[str] = None
    side: Optional[int] = None
    unique_line: Optional[str] = None
    unique_line_vs: Optional[str] = None
    unique_role: Optional[str] = None
    unique_role_vs: Optional[str] = None
    game_id: Optional[str] = None
    match_id: Optional[str] = None
    game_team_id: Optional[str] = None
    game_role_id: Optional[str] = None
    game_role_id_vs: Optional[str] = None
    stats_page: Optional[str] = None

    @property
    def player_name(self) -> Optional[str]:
        """Returns the player name without disambiguation."""
        if not self.link:
            return None
        # Remove disambiguation from link (everything after the first space)
        return self.link.split()[0] if self.link else None

    @property
    def kda_ratio(self) -> Optional[float]:
        """Returns the KDA ratio: (Kills + Assists) / Deaths."""
        if self.kills is None or self.assists is None:
            return None
        if self.deaths is None or self.deaths == 0:
            return float("inf") if (self.kills or 0) + (self.assists or 0) > 0 else 0
        return (self.kills + self.assists) / self.deaths

    @property
    def kill_participation(self) -> Optional[float]:
        """Returns kill participation as a percentage: (Kills + Assists) / Team Kills."""
        if (
            self.kills is None
            or self.assists is None
            or self.team_kills is None
            or self.team_kills == 0
        ):
            return None
        return ((self.kills + self.assists) / self.team_kills) * 100

    @property
    def gold_share(self) -> Optional[float]:
        """Returns gold share as a percentage: Gold / Team Gold."""
        if self.gold is None or self.team_gold is None or self.team_gold == 0:
            return None
        return (self.gold / self.team_gold) * 100

    @property
    def damage_share(self) -> Optional[float]:
        """Returns damage share if team damage data is available."""
        # Note: Team damage would need to be calculated from all team members
        # This is a placeholder for potential future enhancement
        return None

    @property
    def cs_per_minute(self) -> Optional[float]:
        """Returns CS per minute if game duration is available."""
        # Note: Game duration would need to be extracted from time field or calculated
        # This is a placeholder for potential future enhancement
        return None

    @property
    def gold_per_minute(self) -> Optional[float]:
        """Returns gold per minute if game duration is available."""
        # Note: Game duration would need to be extracted from time field or calculated
        # This is a placeholder for potential future enhancement
        return None

    @property
    def did_win(self) -> Optional[bool]:
        """Returns True if the player won the game."""
        if not self.player_win:
            return None
        return self.player_win.lower() in ["yes", "true", "1"]

    @property
    def multikill_potential(self) -> Optional[str]:
        """Estimates multikill potential based on kills and assists."""
        if self.kills is None:
            return None
        if self.kills >= 5:
            return "Pentakill potential"
        elif self.kills >= 4:
            return "Quadrakill potential"
        elif self.kills >= 3:
            return "Triplekill potential"
        elif self.kills >= 2:
            return "Doublekill potential"
        return "Standard performance"

    @property
    def performance_grade(self) -> Optional[str]:
        """Returns a performance grade based on KDA and kill participation."""
        kda = self.kda_ratio
        kp = self.kill_participation

        if kda is None:
            return None

        # Grading system based on typical pro performance metrics
        if kda >= 4.0 and (kp is None or kp >= 70):
            return "S"
        elif kda >= 2.5 and (kp is None or kp >= 60):
            return "A"
        elif kda >= 1.5 and (kp is None or kp >= 50):
            return "B"
        elif kda >= 1.0:
            return "C"
        else:
            return "D"


def _parse_scoreboard_player_data(data: dict) -> ScoreboardPlayer:
    """Parses raw API response data into a ScoreboardPlayer object."""

    def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(date_str) if date_str else None
        except (ValueError, AttributeError):
            return None

    def parse_int(value: Optional[str]) -> Optional[int]:
        try:
            return int(value) if value and str(value).strip() else None
        except (ValueError, TypeError):
            return None

    def parse_list(value: Optional[str], delimiter: str = ",") -> Optional[List[str]]:
        if not value:
            return None
        return [item.strip() for item in value.split(delimiter) if item.strip()]

    return ScoreboardPlayer(
        overview_page=data.get("OverviewPage"),
        name=data.get("Name"),
        link=data.get("Link"),
        champion=data.get("Champion"),
        kills=parse_int(data.get("Kills")),
        deaths=parse_int(data.get("Deaths")),
        assists=parse_int(data.get("Assists")),
        summoner_spells=parse_list(data.get("SummonerSpells"), ","),
        gold=parse_int(data.get("Gold")),
        cs=parse_int(data.get("CS")),
        damage_to_champions=parse_int(data.get("DamageToChampions")),
        vision_score=parse_int(data.get("VisionScore")),
        items=parse_list(data.get("Items"), ";"),
        trinket=data.get("Trinket"),
        keystone_mastery=data.get("KeystoneMastery"),
        keystone_rune=data.get("KeystoneRune"),
        primary_tree=data.get("PrimaryTree"),
        secondary_tree=data.get("SecondaryTree"),
        runes=data.get("Runes"),
        team_kills=parse_int(data.get("TeamKills")),
        team_gold=parse_int(data.get("TeamGold")),
        team=data.get("Team"),
        team_vs=data.get("TeamVs"),
        time=parse_datetime(data.get("Time")),
        player_win=data.get("PlayerWin"),
        datetime_utc=parse_datetime(data.get("DateTime_UTC")),
        dst=data.get("DST"),
        tournament=data.get("Tournament") or data.get("OverviewPage"),
        role=data.get("Role"),
        role_number=parse_int(data.get("Role_Number")),
        ingame_role=data.get("IngameRole"),
        side=parse_int(data.get("Side")),
        unique_line=data.get("UniqueLine"),
        unique_line_vs=data.get("UniqueLineVs"),
        unique_role=data.get("UniqueRole"),
        unique_role_vs=data.get("UniqueRoleVs"),
        game_id=data.get("GameId"),
        match_id=data.get("MatchId"),
        game_team_id=data.get("GameTeamId"),
        game_role_id=data.get("GameRoleId"),
        game_role_id_vs=data.get("GameRoleIdVs"),
        stats_page=data.get("StatsPage"),
    )


def get_scoreboard_players(
    tournament: str = None,
    player: str = None,
    team: str = None,
    champion: str = None,
    game_id: str = None,
    role: str = None,
    limit: int = None,
    **kwargs,
) -> List[ScoreboardPlayer]:
    """Returns player performance statistics from ScoreboardPlayers table.

    Args:
        tournament: Tournament to filter by (uses OverviewPage field internally)
        player: Player name to filter by (searches in Link field)
        team: Team name to filter by
        champion: Champion name to filter by
        game_id: Specific game ID to filter by
        role: Player role to filter by
        limit: Maximum number of results to return (applied after query)
        **kwargs: Additional query parameters

    Returns:
        A list of ScoreboardPlayer objects

    Raises:
        RuntimeError: If the Leaguepedia query fails
        
    Note:
        The tournament parameter filters using the OverviewPage field rather than 
        the Tournament field, as the Tournament field is often empty in the 
        ScoreboardPlayers table. The tournament data in returned objects is 
        populated from OverviewPage when Tournament is empty.
    """
    try:
        where_conditions = []

        if tournament:
            escaped_tournament = tournament.replace("'", "''")
            where_conditions.append(
                f"ScoreboardPlayers.OverviewPage='{escaped_tournament}'"
            )

        if player:
            escaped_player = player.replace("'", "''")
            where_conditions.append(f"ScoreboardPlayers.Link LIKE '%{escaped_player}%'")

        if team:
            escaped_team = team.replace("'", "''")
            where_conditions.append(f"ScoreboardPlayers.Team='{escaped_team}'")

        if champion:
            escaped_champion = champion.replace("'", "''")
            where_conditions.append(f"ScoreboardPlayers.Champion='{escaped_champion}'")

        if game_id:
            escaped_game_id = game_id.replace("'", "''")
            where_conditions.append(f"ScoreboardPlayers.GameId='{escaped_game_id}'")

        if role:
            escaped_role = role.replace("'", "''")
            where_conditions.append(f"ScoreboardPlayers.Role='{escaped_role}'")

        where_clause = " AND ".join(where_conditions) if where_conditions else None

        # Remove limit from kwargs to avoid conflicts with leaguepedia.query internal limit
        clean_kwargs = kwargs.copy()
        clean_kwargs.pop('limit', None)

        players = leaguepedia.query(
            tables="ScoreboardPlayers",
            fields=",".join(f"ScoreboardPlayers.{field}" for field in scoreboard_players_fields),
            where=where_clause,
            order_by="ScoreboardPlayers.DateTime_UTC DESC",
            **clean_kwargs,
        )

        parsed_players = [_parse_scoreboard_player_data(player) for player in players]
        
        # Apply limit after parsing if specified
        return parsed_players[:limit] if limit else parsed_players

    except Exception as e:
        raise RuntimeError(f"Failed to fetch scoreboard players: {str(e)}")


def get_player_match_history(
    player: str, limit: int = 20, **kwargs
) -> List[ScoreboardPlayer]:
    """Returns recent match history for a specific player.

    Args:
        player: Player name
        limit: Maximum number of matches to return
        **kwargs: Additional query parameters

    Returns:
        A list of ScoreboardPlayer objects representing recent matches
    """
    # Get all matches and then limit the results
    players = get_scoreboard_players(player=player, **kwargs)
    return players[:limit] if limit else players


def get_team_match_performance(
    team: str, tournament: str = None, **kwargs
) -> List[ScoreboardPlayer]:
    """Returns match performance for all players of a specific team.

    Args:
        team: Team name
        tournament: Tournament to filter by (optional)
        **kwargs: Additional query parameters

    Returns:
        A list of ScoreboardPlayer objects for the team
    """
    return get_scoreboard_players(team=team, tournament=tournament, **kwargs)


def get_champion_performance_stats(
    champion: str, tournament: str = None, role: str = None, **kwargs
) -> List[ScoreboardPlayer]:
    """Returns performance statistics for a specific champion.

    Args:
        champion: Champion name
        tournament: Tournament to filter by (optional)
        role: Role to filter by (optional)
        **kwargs: Additional query parameters

    Returns:
        A list of ScoreboardPlayer objects for the champion
    """
    return get_scoreboard_players(
        champion=champion, tournament=tournament, role=role, **kwargs
    )


def get_game_scoreboard(game_id: str, **kwargs) -> List[ScoreboardPlayer]:
    """Returns the complete scoreboard for a specific game.

    Args:
        game_id: Game identifier
        **kwargs: Additional query parameters

    Returns:
        A list of ScoreboardPlayer objects (typically 10 players)
    """
    return get_scoreboard_players(game_id=game_id, **kwargs)


def get_tournament_mvp_candidates(
    tournament: str, min_games: int = 5, **kwargs
) -> List[ScoreboardPlayer]:
    """Returns potential MVP candidates based on performance metrics.

    Args:
        tournament: Tournament name
        min_games: Minimum games played to be considered
        **kwargs: Additional query parameters

    Returns:
        A list of ScoreboardPlayer objects sorted by performance
    """
    # Remove any conflicting limit parameter from kwargs
    kwargs_clean = kwargs.copy()
    kwargs_clean.pop('limit', None)
    
    # Get all players from tournament
    players = get_scoreboard_players(tournament=tournament, **kwargs_clean)

    # Filter by minimum games and sort by performance grade and KDA
    filtered_players = []
    player_stats = {}

    # Aggregate stats per player
    for player in players:
        if not player.player_name:
            continue

        if player.player_name not in player_stats:
            player_stats[player.player_name] = {
                "games": [],
                "total_kills": 0,
                "total_deaths": 0,
                "total_assists": 0,
                "wins": 0,
            }

        stats = player_stats[player.player_name]
        stats["games"].append(player)

        if player.kills:
            stats["total_kills"] += player.kills
        if player.deaths:
            stats["total_deaths"] += player.deaths
        if player.assists:
            stats["total_assists"] += player.assists
        if player.did_win:
            stats["wins"] += 1

    # Return players who meet minimum games criteria, with best recent performance
    for player_name, stats in player_stats.items():
        if len(stats["games"]) >= min_games:
            # Get the most recent high-performance game
            best_game = max(
                stats["games"],
                key=lambda x: (x.kda_ratio or 0, x.kill_participation or 0),
            )
            filtered_players.append(best_game)

    # Sort by performance metrics
    return sorted(
        filtered_players,
        key=lambda x: (x.kda_ratio or 0, x.kill_participation or 0),
        reverse=True,
    )


def get_role_performance_comparison(
    tournament: str, role: str, **kwargs
) -> List[ScoreboardPlayer]:
    """Returns performance comparison for players in a specific role.

    Args:
        tournament: Tournament name
        role: Role to compare (e.g., 'Mid', 'ADC', 'Support')
        **kwargs: Additional query parameters

    Returns:
        A list of ScoreboardPlayer objects for role comparison
    """
    # Remove conflicting order_by from kwargs if present
    kwargs_copy = kwargs.copy()
    kwargs_copy.pop("order_by", None)

    return get_scoreboard_players(tournament=tournament, role=role, **kwargs_copy)
