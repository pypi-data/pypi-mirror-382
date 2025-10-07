import dataclasses
from typing import List, Optional
from datetime import datetime

from leaguepedia_parser_thomasbarrepitous.site.leaguepedia import leaguepedia
from leaguepedia_parser_thomasbarrepitous.transmuters.field_names import (
    contracts_fields,
)


@dataclasses.dataclass
class Contract:
    """Represents a contract from Leaguepedia's Contracts table.

    Attributes:
        player: Player name (String)
        team: Team name (String)
        contract_end: Contract expiration date (Date)
        contract_end_text: Textual representation of contract end (String)
        is_removal: Whether this is a contract removal entry (Boolean)
        news_id: News source identifier (String)
    """

    player: Optional[str] = None
    team: Optional[str] = None
    contract_end: Optional[datetime] = None
    contract_end_text: Optional[str] = None
    is_removal: Optional[bool] = None
    news_id: Optional[str] = None

    @property
    def is_active(self) -> Optional[bool]:
        """Returns True if the contract is currently active (not expired and not a removal)."""
        if self.is_removal:
            return False
        if self.contract_end:
            return self.contract_end > datetime.now()
        return None

    @property
    def is_expired(self) -> Optional[bool]:
        """Returns True if the contract has expired."""
        if self.contract_end:
            return self.contract_end <= datetime.now()
        return None

    @property
    def days_until_expiry(self) -> Optional[int]:
        """Returns the number of days until contract expiry (negative if expired)."""
        if self.contract_end:
            delta = self.contract_end - datetime.now()
            return delta.days
        return None


def _parse_contract_data(data: dict) -> Contract:
    """Parses raw API response data into a Contract object."""

    def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(date_str) if date_str else None
        except (ValueError, AttributeError):
            return None

    def parse_bool(value: Optional[str]) -> Optional[bool]:
        if isinstance(value, bool):
            return value
        return value == "1" if value else None

    return Contract(
        player=data.get("Player"),
        team=data.get("Team"),
        contract_end=parse_datetime(data.get("ContractEnd")),
        contract_end_text=data.get("ContractEndText"),
        is_removal=parse_bool(data.get("IsRemoval")),
        news_id=data.get("NewsId"),
    )


def get_contracts(
    player: str = None,
    team: str = None,
    include_removals: bool = False,
    active_only: bool = False,
    **kwargs,
) -> List[Contract]:
    """Returns contract information from Leaguepedia.

    Args:
        player: Player name to filter by
        team: Team name to filter by
        include_removals: Whether to include contract removal entries
        active_only: Whether to only return currently active contracts
        **kwargs: Additional query parameters

    Returns:
        A list of Contract objects

    Raises:
        RuntimeError: If the Leaguepedia query fails
    """
    try:
        where_conditions = []

        if player:
            escaped_player = player.replace("'", "''")
            where_conditions.append(f"Contracts.Player='{escaped_player}'")

        if team:
            escaped_team = team.replace("'", "''")
            where_conditions.append(f"Contracts.Team='{escaped_team}'")

        if not include_removals:
            where_conditions.append(
                "Contracts.IsRemoval IS NULL OR Contracts.IsRemoval='0'"
            )

        if active_only:
            current_date = datetime.now().strftime("%Y-%m-%d")
            where_conditions.append(f"Contracts.ContractEnd >= '{current_date}'")
            where_conditions.append(
                "Contracts.IsRemoval IS NULL OR Contracts.IsRemoval='0'"
            )

        where_clause = " AND ".join(where_conditions) if where_conditions else None

        contracts = leaguepedia.query(
            tables="Contracts",
            fields=",".join(contracts_fields),
            where=where_clause,
            order_by="Contracts.ContractEnd DESC",
            **kwargs,
        )

        return [_parse_contract_data(contract) for contract in contracts]

    except Exception as e:
        raise RuntimeError(f"Failed to fetch contracts: {str(e)}")


def get_player_contracts(player: str, **kwargs) -> List[Contract]:
    """Returns all contracts for a specific player.

    Args:
        player: Player name
        **kwargs: Additional query parameters

    Returns:
        A list of Contract objects for the specified player
    """
    return get_contracts(player=player, **kwargs)


def get_team_contracts(
    team: str, active_only: bool = False, **kwargs
) -> List[Contract]:
    """Returns all contracts for a specific team.

    Args:
        team: Team name
        active_only: Whether to only return currently active contracts
        **kwargs: Additional query parameters

    Returns:
        A list of Contract objects for the specified team
    """
    return get_contracts(team=team, active_only=active_only, **kwargs)


def get_active_contracts(team: str = None, **kwargs) -> List[Contract]:
    """Returns currently active contracts.

    Args:
        team: Team to filter by (optional)
        **kwargs: Additional query parameters

    Returns:
        A list of active Contract objects
    """
    return get_contracts(team=team, active_only=True, **kwargs)


def get_expiring_contracts(
    days: int = 30, team: str = None, **kwargs
) -> List[Contract]:
    """Returns contracts expiring within the specified number of days.

    Args:
        days: Number of days to look ahead (default: 30)
        team: Team to filter by (optional)
        **kwargs: Additional query parameters

    Returns:
        A list of Contract objects expiring soon
    """
    try:
        where_conditions = []

        if team:
            escaped_team = team.replace("'", "''")
            where_conditions.append(f"Contracts.Team='{escaped_team}'")

        # Get contracts expiring within the specified days
        current_date = datetime.now().strftime("%Y-%m-%d")
        end_date = datetime.now().replace(hour=23, minute=59, second=59).timestamp() + (
            days * 24 * 60 * 60
        )
        end_date_str = datetime.fromtimestamp(end_date).strftime("%Y-%m-%d")

        where_conditions.append(f"Contracts.ContractEnd >= '{current_date}'")
        where_conditions.append(f"Contracts.ContractEnd <= '{end_date_str}'")
        where_conditions.append(
            "Contracts.IsRemoval IS NULL OR Contracts.IsRemoval='0'"
        )

        where_clause = " AND ".join(where_conditions)

        contracts = leaguepedia.query(
            tables="Contracts",
            fields=",".join(contracts_fields),
            where=where_clause,
            order_by="Contracts.ContractEnd ASC",
            **kwargs,
        )

        return [_parse_contract_data(contract) for contract in contracts]

    except Exception as e:
        raise RuntimeError(f"Failed to fetch expiring contracts: {str(e)}")


def get_contract_removals(
    player: str = None, team: str = None, **kwargs
) -> List[Contract]:
    """Returns contract removal entries.

    Args:
        player: Player to filter by (optional)
        team: Team to filter by (optional)
        **kwargs: Additional query parameters

    Returns:
        A list of Contract objects representing removals
    """
    try:
        where_conditions = ["Contracts.IsRemoval='1'"]

        if player:
            escaped_player = player.replace("'", "''")
            where_conditions.append(f"Contracts.Player='{escaped_player}'")

        if team:
            escaped_team = team.replace("'", "''")
            where_conditions.append(f"Contracts.Team='{escaped_team}'")

        where_clause = " AND ".join(where_conditions)

        contracts = leaguepedia.query(
            tables="Contracts",
            fields=",".join(contracts_fields),
            where=where_clause,
            order_by="Contracts.ContractEnd DESC",
            **kwargs,
        )

        return [_parse_contract_data(contract) for contract in contracts]

    except Exception as e:
        raise RuntimeError(f"Failed to fetch contract removals: {str(e)}")
