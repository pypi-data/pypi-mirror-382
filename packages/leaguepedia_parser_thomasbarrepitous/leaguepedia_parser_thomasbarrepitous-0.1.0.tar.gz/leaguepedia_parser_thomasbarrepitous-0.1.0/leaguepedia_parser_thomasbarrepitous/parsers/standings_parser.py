import dataclasses
from typing import List, Optional

from leaguepedia_parser_thomasbarrepitous.site.leaguepedia import leaguepedia
from leaguepedia_parser_thomasbarrepitous.transmuters.field_names import (
    standings_fields,
)


@dataclasses.dataclass
class Standing:
    """Represents a team's standing from Leaguepedia's Standings table.

    Attributes:
        overview_page: Tournament overview page
        team: Team name
        page_and_team: Combined page and team identifier
        n: Row number or identifier
        place: Final placement/rank
        win_series: Number of series wins
        loss_series: Number of series losses
        tie_series: Number of series ties
        win_games: Individual game wins
        loss_games: Individual game losses
        points: Points earned in the standings
        points_tiebreaker: Tiebreaker points (float)
        streak: Current win/loss streak count
        streak_direction: Direction of streak ("W" for win, "L" for loss)
    """

    overview_page: Optional[str] = None
    team: Optional[str] = None
    page_and_team: Optional[str] = None
    n: Optional[int] = None
    place: Optional[int] = None
    win_series: Optional[int] = None
    loss_series: Optional[int] = None
    tie_series: Optional[int] = None
    win_games: Optional[int] = None
    loss_games: Optional[int] = None
    points: Optional[int] = None
    points_tiebreaker: Optional[float] = None
    streak: Optional[int] = None
    streak_direction: Optional[str] = None

    @property
    def series_win_rate(self) -> Optional[float]:
        """Calculate series win rate as a percentage."""
        if self.win_series is not None and self.loss_series is not None:
            total_series = self.win_series + self.loss_series
            if total_series > 0:
                return (self.win_series / total_series) * 100
        return None

    @property
    def game_win_rate(self) -> Optional[float]:
        """Calculate game win rate as a percentage."""
        if self.win_games is not None and self.loss_games is not None:
            total_games = self.win_games + self.loss_games
            if total_games > 0:
                return (self.win_games / total_games) * 100
        return None

    @property
    def total_series_played(self) -> Optional[int]:
        """Total series played."""
        if self.win_series is not None and self.loss_series is not None:
            ties = self.tie_series or 0
            return self.win_series + self.loss_series + ties
        return None

    @property
    def total_games_played(self) -> Optional[int]:
        """Total games played."""
        if self.win_games is not None and self.loss_games is not None:
            return self.win_games + self.loss_games
        return None


def _parse_standing_data(data: dict) -> Standing:
    """Parses raw API response data into a Standing object."""

    def parse_int(value: Optional[str]) -> Optional[int]:
        try:
            return (
                int(value)
                if value and str(value).strip() and str(value).strip().isdigit()
                else None
            )
        except (ValueError, TypeError):
            return None

    def parse_float(value: Optional[str]) -> Optional[float]:
        try:
            return float(value) if value and str(value).strip() else None
        except (ValueError, TypeError):
            return None

    return Standing(
        overview_page=data.get("OverviewPage"),
        team=data.get("Team"),
        page_and_team=data.get("PageAndTeam"),
        n=parse_int(data.get("N")),
        place=parse_int(data.get("Place")),
        win_series=parse_int(data.get("WinSeries")),
        loss_series=parse_int(data.get("LossSeries")),
        tie_series=parse_int(data.get("TieSeries")),
        win_games=parse_int(data.get("WinGames")),
        loss_games=parse_int(data.get("LossGames")),
        points=parse_int(data.get("Points")),
        points_tiebreaker=parse_float(data.get("PointsTiebreaker")),
        streak=parse_int(data.get("Streak")),
        streak_direction=data.get("StreakDirection"),
    )


def get_standings(
    overview_page: str = None,
    team: str = None,
    **kwargs,
) -> List[Standing]:
    """Returns standings information from Leaguepedia.

    Args:
        overview_page: Tournament overview page to filter by
        team: Team name to filter by
        **kwargs: Additional query parameters

    Returns:
        A list of Standing objects containing team standings

    Raises:
        RuntimeError: If the Leaguepedia query fails
    """
    try:
        where_conditions = []

        if overview_page:
            escaped_overview_page = overview_page.replace("'", "''")
            where_conditions.append(f"Standings.OverviewPage='{escaped_overview_page}'")

        if team:
            escaped_team = team.replace("'", "''")
            where_conditions.append(f"Standings.Team='{escaped_team}'")

        where_clause = " AND ".join(where_conditions) if where_conditions else None

        standings = leaguepedia.query(
            tables="Standings",
            fields=",".join(standings_fields),
            where=where_clause,
            order_by="Standings.Place",
            **kwargs,
        )

        return [_parse_standing_data(standing) for standing in standings]

    except Exception as e:
        raise RuntimeError(f"Failed to fetch standings: {str(e)}")


def get_tournament_standings(overview_page: str, **kwargs) -> List[Standing]:
    """Returns standings for a specific tournament.

    Args:
        overview_page: Tournament overview page
        **kwargs: Additional query parameters

    Returns:
        A list of Standing objects sorted by place
    """
    return get_standings(overview_page=overview_page, **kwargs)


def get_team_standings(team: str, **kwargs) -> List[Standing]:
    """Returns standings history for a specific team.

    Args:
        team: Team name
        **kwargs: Additional query parameters

    Returns:
        A list of Standing objects for the specified team
    """
    return get_standings(team=team, **kwargs)


def get_standings_by_overview_page(overview_page: str, **kwargs) -> List[Standing]:
    """Returns standings for a specific tournament overview page.

    Args:
        overview_page: Tournament overview page
        **kwargs: Additional query parameters

    Returns:
        A list of Standing objects for the specified tournament
    """
    return get_standings(overview_page=overview_page, **kwargs)
