import dataclasses
from typing import List, Optional
from datetime import datetime

from leaguepedia_parser_thomasbarrepitous.site.leaguepedia import leaguepedia
from leaguepedia_parser_thomasbarrepitous.transmuters.field_names import (
    champions_fields,
)


@dataclasses.dataclass
class Champion:
    """Represents a League of Legends champion from Leaguepedia's Champions table.

    Attributes:
        name: Champion name
        title: Champion title/subtitle
        release_date: Date the champion was released
        be: Blue Essence cost
        rp: Riot Points cost
        attributes: List of champion attributes (e.g., Fighter, Tank)
        resource: Resource type (Mana, Energy, etc.)
        real_name: Real name of the champion
        health: Base health
        hp_level: Health growth per level
        hp_regen: Base health regeneration
        hp_regen_level: Health regen growth per level
        mana: Base mana
        mana_level: Mana growth per level
        mana_regen: Base mana regeneration
        mana_regen_level: Mana regen growth per level
        energy: Base energy (if energy champion)
        energy_regen: Energy regeneration
        movespeed: Base movement speed
        attack_damage: Base attack damage
        ad_level: AD growth per level
        attack_speed: Base attack speed
        as_level: AS growth per level
        attack_range: Attack range
        armor: Base armor
        armor_level: Armor growth per level
        magic_resist: Base magic resistance
        magic_resist_level: MR growth per level
        key_integer: Unique numeric key for the champion
    """

    name: Optional[str] = None
    title: Optional[str] = None
    release_date: Optional[datetime] = None
    be: Optional[int] = None
    rp: Optional[int] = None
    attributes: Optional[str] = None  # Comma-delimited string
    resource: Optional[str] = None
    real_name: Optional[str] = None
    health: Optional[float] = None
    hp_level: Optional[float] = None
    hp_regen: Optional[float] = None
    hp_regen_level: Optional[float] = None
    mana: Optional[float] = None
    mana_level: Optional[float] = None
    mana_regen: Optional[float] = None
    mana_regen_level: Optional[float] = None
    energy: Optional[float] = None
    energy_regen: Optional[float] = None
    movespeed: Optional[float] = None
    attack_damage: Optional[float] = None
    ad_level: Optional[float] = None
    attack_speed: Optional[float] = None
    as_level: Optional[float] = None
    attack_range: Optional[float] = None
    armor: Optional[float] = None
    armor_level: Optional[float] = None
    magic_resist: Optional[float] = None
    magic_resist_level: Optional[float] = None
    key_integer: Optional[int] = None

    @property
    def is_melee(self) -> Optional[bool]:
        """Returns True if champion is melee (attack range <= 200), False if ranged."""
        if self.attack_range is not None:
            return self.attack_range <= 200
        return None

    @property
    def is_ranged(self) -> Optional[bool]:
        """Returns True if champion is ranged (attack range > 200), False if melee."""
        if self.attack_range is not None:
            return self.attack_range > 200
        return None

    @property
    def attributes_list(self) -> list:
        """Returns attributes as a list."""
        if self.attributes:
            return [attr.strip() for attr in self.attributes.split(",") if attr.strip()]
        return []


def _parse_champion_data(data: dict) -> Champion:
    """Parses raw API response data into a Champion object."""

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

    def parse_float(value: Optional[str]) -> Optional[float]:
        try:
            return float(value) if value and str(value).strip() else None
        except (ValueError, TypeError):
            return None

    return Champion(
        name=data.get("Name"),
        title=data.get("Title"),
        release_date=parse_datetime(data.get("ReleaseDate")),
        be=parse_int(data.get("BE")),
        rp=parse_int(data.get("RP")),
        attributes=data.get("Attributes"),
        resource=data.get("Resource"),
        real_name=data.get("RealName"),
        health=parse_float(data.get("Health")),
        hp_level=parse_float(data.get("HPLevel")),
        hp_regen=parse_float(data.get("HPRegen")),
        hp_regen_level=parse_float(data.get("HPRegenLevel")),
        mana=parse_float(data.get("Mana")),
        mana_level=parse_float(data.get("ManaLevel")),
        mana_regen=parse_float(data.get("ManaRegen")),
        mana_regen_level=parse_float(data.get("ManaRegenLevel")),
        energy=parse_float(data.get("Energy")),
        energy_regen=parse_float(data.get("EnergyRegen")),
        movespeed=parse_float(data.get("Movespeed")),
        attack_damage=parse_float(data.get("AttackDamage")),
        ad_level=parse_float(data.get("ADLevel")),
        attack_speed=parse_float(data.get("AttackSpeed")),
        as_level=parse_float(data.get("ASLevel")),
        attack_range=parse_float(data.get("AttackRange")),
        armor=parse_float(data.get("Armor")),
        armor_level=parse_float(data.get("ArmorLevel")),
        magic_resist=parse_float(data.get("MagicResist")),
        magic_resist_level=parse_float(data.get("MagicResistLevel")),
        key_integer=parse_int(data.get("KeyInteger")),
    )


def get_champions(
    resource: str = None, attributes: str = None, **kwargs
) -> List[Champion]:
    """Returns champion information from Leaguepedia.

    Args:
        resource: Resource type to filter by (e.g., "Mana", "Energy")
        attributes: Attribute to filter by (e.g., "Fighter", "Tank", "Assassin")
        **kwargs: Additional query parameters

    Returns:
        A list of Champion objects

    Raises:
        RuntimeError: If the Leaguepedia query fails
    """
    try:
        where_conditions = []

        if resource:
            escaped_resource = resource.replace("'", "''")
            where_conditions.append(f"Champions.Resource='{escaped_resource}'")

        if attributes:
            escaped_attributes = attributes.replace("'", "''")
            where_conditions.append(
                f"Champions.Attributes LIKE '%{escaped_attributes}%'"
            )

        where_clause = " AND ".join(where_conditions) if where_conditions else None

        champions = leaguepedia.query(
            tables="Champions",
            fields=",".join(champions_fields),
            where=where_clause,
            order_by="Champions.Name",
            **kwargs,
        )

        return [_parse_champion_data(champion) for champion in champions]

    except Exception as e:
        raise RuntimeError(f"Failed to fetch champions: {str(e)}")


def get_champion_by_name(champion_name: str) -> Optional[Champion]:
    """Returns a specific champion by name.

    Args:
        champion_name: Exact champion name

    Returns:
        Champion object if found, None otherwise

    Raises:
        RuntimeError: If the Leaguepedia query fails
    """
    try:
        escaped_name = champion_name.replace("'", "''")
        champions = leaguepedia.query(
            tables="Champions",
            fields=",".join(champions_fields),
            where=f"Champions.Name='{escaped_name}'",
        )

        return _parse_champion_data(champions[0]) if champions else None

    except Exception as e:
        raise RuntimeError(f"Failed to fetch champion {champion_name}: {str(e)}")


def get_champions_by_attributes(attributes: str) -> List[Champion]:
    """Returns all champions with a specific attribute.

    Args:
        attributes: Attribute (e.g., "Fighter", "Tank", "Assassin", "Mage", "Support", "Marksman")

    Returns:
        List of Champion objects with the specified attribute
    """
    return get_champions(attributes=attributes)


def get_champions_by_resource(resource: str) -> List[Champion]:
    """Returns all champions with a specific resource type.

    Args:
        resource: Resource type (e.g., "Mana", "Energy", "Fury", "None")

    Returns:
        List of Champion objects with the specified resource
    """
    return get_champions(resource=resource)


def get_melee_champions() -> List[Champion]:
    """Returns all melee champions (attack range <= 200)."""
    champions = get_champions()
    return [champ for champ in champions if champ.is_melee]


def get_ranged_champions() -> List[Champion]:
    """Returns all ranged champions (attack range > 200)."""
    champions = get_champions()
    return [champ for champ in champions if champ.is_ranged]
