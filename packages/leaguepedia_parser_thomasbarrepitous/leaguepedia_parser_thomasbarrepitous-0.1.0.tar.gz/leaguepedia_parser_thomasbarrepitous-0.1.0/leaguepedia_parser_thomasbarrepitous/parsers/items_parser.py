import dataclasses
from typing import List, Optional

from leaguepedia_parser_thomasbarrepitous.site.leaguepedia import leaguepedia
from leaguepedia_parser_thomasbarrepitous.transmuters.field_names import items_fields


@dataclasses.dataclass
class Item:
    """Represents a League of Legends item from Leaguepedia's Items table.

    Attributes:
        name: Item name
        tier: Item tier (Basic, Epic, Legendary, etc.)
        riot_id: Riot's internal item ID
        recipe: Required components (+ delimited)
        cost: Combine cost
        total_cost: Total cost to purchase
        ad: Attack damage
        life_steal: Life steal percentage
        health: Health points
        hp_regen: Health regeneration
        armor: Armor points
        mr: Magic resistance points
        attack_damage: Attack damage (duplicate field)
        crit: Critical strike chance
        attack_speed: Attack speed percentage
        armor_pen: Armor penetration
        lethality: Lethality
        attack_range: Attack range bonus
        mana: Mana points
        mana_regen: Mana regeneration
        energy: Energy points
        energy_regen: Energy regeneration
        ap: Ability power
        cdr: Cooldown reduction
        ability_haste: Ability haste
        omnivamp: Omnivamp percentage
        phys_vamp: Physical vamp percentage
        spell_vamp: Spell vamp percentage
        mpen: Magic penetration
        movespeed_flat: Flat movement speed
        movespeed_percent: Movement speed percentage
        tenacity: Tenacity percentage
        gold_gen: Gold generation
        on_hit: On-hit damage
        bonus_hp: Bonus health
        healing: Healing power
        hs_power: Heal and shield power
        slow_resist: Slow resistance
    """

    name: Optional[str] = None
    tier: Optional[str] = None
    riot_id: Optional[int] = None
    recipe: Optional[str] = None
    cost: Optional[int] = None
    total_cost: Optional[int] = None
    ad: Optional[int] = None
    life_steal: Optional[int] = None
    health: Optional[int] = None
    hp_regen: Optional[int] = None
    armor: Optional[int] = None
    mr: Optional[int] = None
    attack_damage: Optional[int] = None
    crit: Optional[int] = None
    attack_speed: Optional[int] = None
    armor_pen: Optional[int] = None
    lethality: Optional[int] = None
    attack_range: Optional[int] = None
    mana: Optional[int] = None
    mana_regen: Optional[int] = None
    energy: Optional[int] = None
    energy_regen: Optional[int] = None
    ap: Optional[int] = None
    cdr: Optional[int] = None
    ability_haste: Optional[int] = None
    omnivamp: Optional[int] = None
    phys_vamp: Optional[int] = None
    spell_vamp: Optional[int] = None
    mpen: Optional[int] = None
    movespeed_flat: Optional[int] = None
    movespeed_percent: Optional[int] = None
    tenacity: Optional[int] = None
    gold_gen: Optional[int] = None
    on_hit: Optional[int] = None
    bonus_hp: Optional[int] = None
    healing: Optional[int] = None
    hs_power: Optional[int] = None
    slow_resist: Optional[int] = None

    @property
    def provides_ad(self) -> bool:
        """Returns True if item provides attack damage."""
        return bool(
            (self.ad and self.ad > 0) or (self.attack_damage and self.attack_damage > 0)
        )

    @property
    def provides_ap(self) -> bool:
        """Returns True if item provides ability power."""
        return bool(self.ap and self.ap > 0)

    @property
    def provides_armor(self) -> bool:
        """Returns True if item provides armor."""
        return bool(self.armor and self.armor > 0)

    @property
    def provides_mr(self) -> bool:
        """Returns True if item provides magic resistance."""
        return bool(self.mr and self.mr > 0)

    @property
    def provides_health(self) -> bool:
        """Returns True if item provides health."""
        return bool(
            (self.health and self.health > 0) or (self.bonus_hp and self.bonus_hp > 0)
        )

    @property
    def provides_mana(self) -> bool:
        """Returns True if item provides mana."""
        return bool(self.mana and self.mana > 0)


def _parse_item_data(data: dict) -> Item:
    """Parses raw API response data into an Item object."""

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

    def parse_bool(value: Optional[str]) -> Optional[bool]:
        return value == "Yes" if value else None

    return Item(
        name=data.get("Name"),
        tier=data.get("Tier"),
        riot_id=parse_int(data.get("RiotId")),
        recipe=data.get("Recipe"),
        cost=parse_int(data.get("Cost")),
        total_cost=parse_int(data.get("TotalCost")),
        ad=parse_int(data.get("AD")),
        life_steal=parse_int(data.get("LifeSteal")),
        health=parse_int(data.get("Health")),
        hp_regen=parse_int(data.get("HPRegen")),
        armor=parse_int(data.get("Armor")),
        mr=parse_int(data.get("MR")),
        attack_damage=parse_int(data.get("AttackDamage")),
        crit=parse_int(data.get("Crit")),
        attack_speed=parse_int(data.get("AttackSpeed")),
        armor_pen=parse_int(data.get("ArmorPen")),
        lethality=parse_int(data.get("Lethality")),
        attack_range=parse_int(data.get("AttackRange")),
        mana=parse_int(data.get("Mana")),
        mana_regen=parse_int(data.get("ManaRegen")),
        energy=parse_int(data.get("Energy")),
        energy_regen=parse_int(data.get("EnergyRegen")),
        ap=parse_int(data.get("AP")),
        cdr=parse_int(data.get("CDR")),
        ability_haste=parse_int(data.get("AbilityHaste")),
        omnivamp=parse_int(data.get("Omnivamp")),
        phys_vamp=parse_int(data.get("PhysVamp")),
        spell_vamp=parse_int(data.get("SpellVamp")),
        mpen=parse_int(data.get("MPen")),
        movespeed_flat=parse_int(data.get("MovespeedFlat")),
        movespeed_percent=parse_int(data.get("MovespeedPercent")),
        tenacity=parse_int(data.get("Tenacity")),
        gold_gen=parse_int(data.get("GoldGen")),
        on_hit=parse_int(data.get("OnHit")),
        bonus_hp=parse_int(data.get("BonusHP")),
        healing=parse_int(data.get("Healing")),
        hs_power=parse_int(data.get("HSPower")),
        slow_resist=parse_int(data.get("SlowResist")),
    )


def get_items(
    tier: str = None,
    **kwargs,
) -> List[Item]:
    """Returns item information from Leaguepedia.

    Args:
        tier: Filter by tier (e.g., "Basic", "Epic", "Legendary")
        **kwargs: Additional query parameters

    Returns:
        A list of Item objects

    Raises:
        RuntimeError: If the Leaguepedia query fails
    """
    try:
        where_conditions = []

        if tier:
            escaped_tier = tier.replace("'", "''")
            where_conditions.append(f"Items.Tier='{escaped_tier}'")

        where_clause = " AND ".join(where_conditions) if where_conditions else None

        items = leaguepedia.query(
            tables="Items",
            fields=",".join(items_fields),
            where=where_clause,
            order_by="Items.Name",
            **kwargs,
        )

        return [_parse_item_data(item) for item in items]

    except Exception as e:
        raise RuntimeError(f"Failed to fetch items: {str(e)}")


def get_item_by_name(item_name: str) -> Optional[Item]:
    """Returns a specific item by name.

    Args:
        item_name: Exact item name

    Returns:
        Item object if found, None otherwise

    Raises:
        RuntimeError: If the Leaguepedia query fails
    """
    try:
        escaped_name = item_name.replace("'", "''")
        items = leaguepedia.query(
            tables="Items",
            fields=",".join(items_fields),
            where=f"Items.Name='{escaped_name}'",
        )

        return _parse_item_data(items[0]) if items else None

    except Exception as e:
        raise RuntimeError(f"Failed to fetch item {item_name}: {str(e)}")


def get_items_by_tier(tier: str) -> List[Item]:
    """Returns all items of a specific tier.

    Args:
        tier: Item tier (e.g., "Basic", "Epic", "Legendary", "Mythic")

    Returns:
        List of Item objects with the specified tier
    """
    return get_items(tier=tier)


def get_ad_items() -> List[Item]:
    """Returns all items that provide attack damage."""
    items = get_items()
    return [item for item in items if item.provides_ad]


def get_ap_items() -> List[Item]:
    """Returns all items that provide ability power."""
    items = get_items()
    return [item for item in items if item.provides_ap]


def get_tank_items() -> List[Item]:
    """Returns all items that provide armor or magic resistance."""
    items = get_items()
    return [item for item in items if item.provides_armor or item.provides_mr]


def get_health_items() -> List[Item]:
    """Returns all items that provide health."""
    items = get_items()
    return [item for item in items if item.provides_health]


def get_mana_items() -> List[Item]:
    """Returns all items that provide mana."""
    items = get_items()
    return [item for item in items if item.provides_mana]


def search_items_by_stat(
    provides_ad: bool = None,
    provides_ap: bool = None,
    provides_armor: bool = None,
    provides_mr: bool = None,
    provides_health: bool = None,
    provides_mana: bool = None,
    **kwargs,
) -> List[Item]:
    """Search items by the stats they provide.

    Args:
        provides_ad: Filter items that provide attack damage
        provides_ap: Filter items that provide ability power
        provides_armor: Filter items that provide armor
        provides_mr: Filter items that provide magic resistance
        provides_health: Filter items that provide health
        provides_mana: Filter items that provide mana
        **kwargs: Additional query parameters

    Returns:
        List of items matching the stat criteria
    """
    items = get_items(**kwargs)

    results = []
    for item in items:
        if provides_ad is not None and item.provides_ad != provides_ad:
            continue
        if provides_ap is not None and item.provides_ap != provides_ap:
            continue
        if provides_armor is not None and item.provides_armor != provides_armor:
            continue
        if provides_mr is not None and item.provides_mr != provides_mr:
            continue
        if provides_health is not None and item.provides_health != provides_health:
            continue
        if provides_mana is not None and item.provides_mana != provides_mana:
            continue
        results.append(item)

    return results
