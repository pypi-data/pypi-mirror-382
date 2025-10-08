import dataclasses
from typing import List, Optional
from datetime import datetime, timedelta
import enum

from leaguepedia_parser_thomasbarrepitous.site.leaguepedia import leaguepedia
from leaguepedia_parser_thomasbarrepitous.transmuters.field_names import (
    roster_changes_fields,
)


class RosterAction(enum.Enum):
    """Enumeration of possible roster actions."""

    ADD = "Add"
    REMOVE = "Remove"
    ROLE_CHANGE = "Role Change"
    SUBSTITUTE = "Substitute"
    LOAN = "Loan"
    TRANSFER = "Transfer"
    RETIREMENT = "Retirement"


@dataclasses.dataclass
class RosterChange:
    """Represents a roster change from Leaguepedia's RosterChanges table.

    Attributes:
        date_sort: Date of the change (Datetime)
        player: Player name (String)
        direction: Direction of the change - Join/Leave (String)
        team: Team name (String)
        roles_ingame: In-game roles (List of String)
        roles_staff: Staff roles (List of String)
        roles: All roles (List of String)
        role_display: Display role (String)
        role: Primary role (String)
        role_modifier: Role modifier (String)
        status: Status of the change (String)
        current_team_priority: Priority level (Integer)
        player_unlinked: Whether player is unlinked (Boolean)
        already_joined: Already joined status (String)
        tournaments: Associated tournaments (List of String)
        source: Source information (Wikitext)
        is_gcd: Is GCD related (Boolean)
        preload: Preload information (String)
        preload_sort_number: Preload sort number (Integer)
        tags: Associated tags (List of String)
        news_id: Related news item ID (String)
        roster_change_id: Roster change identifier (String)
        n_line_in_news: Line number in news (Integer)
    """

    date_sort: Optional[datetime] = None
    player: Optional[str] = None
    direction: Optional[str] = None
    team: Optional[str] = None
    roles_ingame: Optional[List[str]] = None
    roles_staff: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    role_display: Optional[str] = None
    role: Optional[str] = None
    role_modifier: Optional[str] = None
    status: Optional[str] = None
    current_team_priority: Optional[int] = None
    player_unlinked: Optional[bool] = None
    already_joined: Optional[str] = None
    tournaments: Optional[List[str]] = None
    source: Optional[str] = None
    is_gcd: Optional[bool] = None
    preload: Optional[str] = None
    preload_sort_number: Optional[int] = None
    tags: Optional[List[str]] = None
    news_id: Optional[str] = None
    roster_change_id: Optional[str] = None
    n_line_in_news: Optional[int] = None

    @property
    def is_join(self) -> bool:
        """Returns True if this is a join/addition to the team."""
        return bool(self.direction and self.direction.lower() == "join")

    @property
    def is_leave(self) -> bool:
        """Returns True if this is a leave/removal from the team."""
        return bool(self.direction and self.direction.lower() == "leave")

    @property
    def date(self) -> Optional[datetime]:
        """Alias for date_sort for backward compatibility."""
        return self.date_sort

    @property
    def action(self) -> Optional[str]:
        """Alias for direction for backward compatibility."""
        return self.direction

    @property
    def is_addition(self) -> bool:
        """Returns True if this is an addition to the team (backward compatibility)."""
        return self.is_join

    @property
    def is_removal(self) -> bool:
        """Returns True if this is a removal from the team (backward compatibility)."""
        return self.is_leave

    @property
    def is_retirement(self) -> Optional[bool]:
        """Returns True if this is a retirement (backward compatibility)."""
        # Check if this can be detected from status or other fields
        # For now, return None as retirement detection needs more research
        return None


def _parse_roster_change_data(data: dict) -> RosterChange:
    """Parses raw API response data into a RosterChange object."""

    def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(date_str) if date_str else None
        except (ValueError, AttributeError):
            return None

    def parse_bool(value: Optional[str]) -> Optional[bool]:
        if isinstance(value, bool):
            return value
        return value == "Yes" if value else None

    def parse_int(value: Optional[str]) -> Optional[int]:
        try:
            return int(value) if value and str(value).strip() else None
        except (ValueError, TypeError):
            return None

    def parse_list(value: Optional[str], delimiter: str = ",") -> Optional[List[str]]:
        if not value:
            return None
        return [item.strip() for item in value.split(delimiter) if item.strip()]

    return RosterChange(
        date_sort=parse_datetime(data.get("Date_Sort")),
        player=data.get("Player"),
        direction=data.get("Direction"),
        team=data.get("Team"),
        roles_ingame=parse_list(data.get("RolesIngame"), ";"),
        roles_staff=parse_list(data.get("RolesStaff"), ";"),
        roles=parse_list(data.get("Roles"), ";"),
        role_display=data.get("RoleDisplay"),
        role=data.get("Role"),
        role_modifier=data.get("RoleModifier"),
        status=data.get("Status"),
        current_team_priority=parse_int(data.get("CurrentTeamPriority")),
        player_unlinked=parse_bool(data.get("PlayerUnlinked")),
        already_joined=data.get("AlreadyJoined"),
        tournaments=parse_list(data.get("Tournaments")),
        source=data.get("Source"),
        is_gcd=parse_bool(data.get("IsGCD")),
        preload=data.get("Preload"),
        preload_sort_number=parse_int(data.get("PreloadSortNumber")),
        tags=parse_list(data.get("Tags")),
        news_id=data.get("NewsId"),
        roster_change_id=data.get("RosterChangeId"),
        n_line_in_news=parse_int(data.get("N_LineInNews")),
    )


def get_roster_changes(
    team: str = None,
    player: str = None,
    action: str = None,
    tournament: str = None,
    start_date: str = None,
    end_date: str = None,
    **kwargs,
) -> List[RosterChange]:
    """Returns roster change information from Leaguepedia.

    Args:
        team: Team name to filter by
        player: Player name to filter by
        action: Action type to filter by (Add, Remove, etc.)
        tournament: Tournament to filter by
        start_date: Start date for filtering (YYYY-MM-DD format)
        end_date: End date for filtering (YYYY-MM-DD format)
        **kwargs: Additional query parameters

    Returns:
        A list of RosterChange objects

    Raises:
        RuntimeError: If the Leaguepedia query fails
    """
    try:
        where_conditions = []

        if team:
            escaped_team = team.replace("'", "''")
            where_conditions.append(f"RosterChanges.Team='{escaped_team}'")

        if player:
            escaped_player = player.replace("'", "''")
            where_conditions.append(f"RosterChanges.Player='{escaped_player}'")

        if action:
            escaped_action = action.replace("'", "''")
            where_conditions.append(f"RosterChanges.Direction='{escaped_action}'")

        if tournament:
            escaped_tournament = tournament.replace("'", "''")
            where_conditions.append(
                f"RosterChanges.Tournaments LIKE '%{escaped_tournament}%'"
            )

        if start_date:
            where_conditions.append(f"RosterChanges.Date_Sort >= '{start_date}'")

        if end_date:
            where_conditions.append(f"RosterChanges.Date_Sort <= '{end_date}'")

        where_clause = " AND ".join(where_conditions) if where_conditions else None

        changes = leaguepedia.query(
            tables="RosterChanges",
            fields=",".join(roster_changes_fields),
            where=where_clause,
            order_by="RosterChanges.Date_Sort DESC",
            **kwargs,
        )

        return [_parse_roster_change_data(change) for change in changes]

    except Exception as e:
        raise RuntimeError(f"Failed to fetch roster changes: {str(e)}")


def get_team_roster_changes(
    team: str, tournament: str = None, **kwargs
) -> List[RosterChange]:
    """Returns all roster changes for a specific team.

    Args:
        team: Team name
        tournament: Tournament to filter by (optional)
        **kwargs: Additional query parameters

    Returns:
        A list of RosterChange objects for the specified team
    """
    return get_roster_changes(team=team, tournament=tournament, **kwargs)


def get_player_roster_changes(player: str, **kwargs) -> List[RosterChange]:
    """Returns all roster changes for a specific player.

    Args:
        player: Player name
        **kwargs: Additional query parameters

    Returns:
        A list of RosterChange objects for the specified player
    """
    return get_roster_changes(player=player, **kwargs)


def get_recent_roster_changes(
    days: int = 30, team: str = None, **kwargs
) -> List[RosterChange]:
    """Returns recent roster changes within the specified number of days.

    Args:
        days: Number of days to look back (default: 30)
        team: Team to filter by (optional)
        **kwargs: Additional query parameters

    Returns:
        A list of recent RosterChange objects
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    return get_roster_changes(
        team=team, start_date=start_date, end_date=end_date, **kwargs
    )


def get_roster_additions(
    team: str = None, tournament: str = None, **kwargs
) -> List[RosterChange]:
    """Returns roster additions (players joining teams).

    Args:
        team: Team to filter by (optional)
        tournament: Tournament to filter by (optional)
        **kwargs: Additional query parameters

    Returns:
        A list of RosterChange objects representing additions
    """
    return get_roster_changes(team=team, tournament=tournament, action="Join", **kwargs)


def get_roster_removals(
    team: str = None, tournament: str = None, **kwargs
) -> List[RosterChange]:
    """Returns roster removals (players leaving teams).

    Args:
        team: Team to filter by (optional)
        tournament: Tournament to filter by (optional)
        **kwargs: Additional query parameters

    Returns:
        A list of RosterChange objects representing removals
    """
    return get_roster_changes(
        team=team, tournament=tournament, action="Leave", **kwargs
    )


def get_retirements(**kwargs) -> List[RosterChange]:
    """Returns player retirements.

    Args:
        **kwargs: Additional query parameters

    Returns:
        A list of RosterChange objects representing retirements
    """
    # Use the specialized retirement filter
    where_clause = "RosterChanges.IsRetirement='Yes'"

    try:
        changes = leaguepedia.query(
            tables="RosterChanges",
            fields=",".join(roster_changes_fields),
            where=where_clause,
            order_by="RosterChanges.Date_Sort DESC",
            **kwargs,
        )

        return [_parse_roster_change_data(change) for change in changes]

    except Exception as e:
        raise RuntimeError(f"Failed to fetch retirements: {str(e)}")
