# leaguepedia_parser - Enhanced Edition

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Features](https://img.shields.io/badge/features-10_modules-green.svg)](#features)

A **comprehensive** Leaguepedia parser providing easy access to League of Legends esports data. This enhanced fork extends the original with extensive coverage of player statistics, contracts, standings, and performance analytics.

## ✨ Features

**🚀 Advanced Performance Analytics**
- 📊 **Match Statistics** - Individual player KDA, damage, CS, vision score, and performance grading
- 📈 **Performance Analytics** - Kill participation, gold share, multikill analysis, and MVP detection
- 🎯 **Role Comparisons** - Cross-player performance analysis by position and tournament

**Enhanced beyond the original with:**
- 📋 **Contract Tracking** - Player contracts, expiration dates, and team obligations  
- 🏆 **Tournament Standings** - Team rankings, win rates, series/game statistics
- 🎮 **Champion Data** - All champions with attributes, stats, and filtering
- ⚔️ **Items Database** - Complete item catalog with stats and tier filtering  
- 👥 **Roster Changes** - Player transfers, team history, and timeline tracking
- 👤 **Player Profiles** - Comprehensive player information with country, birth dates, status
- 🏟️ **Tournament Rosters** - Team compositions for specific tournaments

**Plus all original functionality:**
- 🎯 Games & match details with picks/bans
- 🏢 Regional & tournament data
- 🖼️ Team assets (logos, thumbnails)

## Install

```bash
# With pip
pip install leaguepedia_parser_thomasbarrepitous

# With Poetry
poetry add leaguepedia_parser_thomasbarrepitous

# Quick verification
python -c "import leaguepedia_parser_thomasbarrepitous as lp; print('✅ Import successful')"
```

## Demo

![Demo](https://raw.githubusercontent.com/mrtolkien/leaguepedia_parser/master/leaguepedia_parser_demo.gif)

## Usage

```python
import leaguepedia_parser_thomasbarrepitous as lp

# Games & Tournaments
regions = lp.get_regions()
# ['Korea', 'Europe', 'North America', 'China', ...]

tournaments = lp.get_tournaments("Korea", year=2020)
# [{'name': 'LCK/2020 Season/Spring Season', 'region': 'Korea'}, ...]

games = lp.get_games("LCK/2020 Season/Spring Season")
# [Game(team1='T1', team2='GenG', winner='T1', date='2020-02-05'), ...]

# Teams & Assets
logo_url = lp.get_team_logo('T1')
# 'https://static.wikia.nocookie.net/lolesports_gamepedia_en/images/t1_logo.png'

team_assets = lp.get_all_team_assets('T1')
# TeamAssets(logo='...', thumbnail='...', team_name='T1')

active_players = lp.get_active_players('T1')
# [TeamPlayer(name='Faker', role='Mid'), TeamPlayer(name='Gumayusi', role='Bot'), ...]

# Players
player = lp.get_player_by_name('Faker')
# PlayerInfo(name='Faker', country='South Korea', birth_date='1996-05-07', status=ACTIVE)

# Tournament Rosters
rosters = lp.get_tournament_rosters('T1', 'LCK/2024 Season/Summer Season')
# [{'Team': 'T1', 'Tournament': 'LCK/2024...', 'Player': 'Faker', 'Role': 'Mid'}, ...]

# Standings
standings = lp.get_tournament_standings("LCK/2024 Season/Summer Season")
# [Standing(team='T1', place=1, win_series=16, loss_series=2), ...]

# Champions
champions = lp.get_champions_by_attributes("Marksman")
# [Champion(name='Jinx', attributes='Marksman', attack_range=525), ...]

champion = lp.get_champion_by_name("Jinx")
# Champion(name='Jinx', attributes='Marksman', attack_range=525, is_ranged=True)

# Items
ad_items = lp.get_ad_items()
# [Item(name='Infinity Edge', ad=70, total_cost=3400), ...]

crit_items = lp.search_items_by_stat("Crit")
# [Item(name='Infinity Edge', crit=20), Item(name='Stormrazor', crit=15), ...]

infinity_edge = lp.get_item_by_name("Infinity Edge")
# Item(name='Infinity Edge', ad=70, crit=20, total_cost=3400, provides_ad=True)

# Roster Changes
roster_changes = lp.get_team_roster_changes("T1")
# [RosterChange(player='Faker', direction='Join', team='T1', date=2013-01-01), ...]

recent_moves = lp.get_recent_roster_changes(days=30)
# [RosterChange(player='Caps', direction='Leave', team='G2', date=2024-11-15), ...]

# 📊 Player Performance Analytics
# Get individual match statistics
faker_matches = lp.get_player_match_history("Faker", limit=5)
for match in faker_matches:
    print(f"{match.champion}: {match.kda_ratio:.1f} KDA, {match.performance_grade} grade")
    # Azir: 20.0 KDA, S grade

# Team performance analysis
t1_performance = lp.get_team_match_performance("T1", tournament="LCK/2024 Season/Summer Season")
avg_kda = sum(p.kda_ratio for p in t1_performance if p.kda_ratio) / len(t1_performance)
# Calculate team statistics: average KDA, win rates, damage distribution

# Champion meta analysis
azir_stats = lp.get_champion_performance_stats("Azir", tournament="LCK/2024 Season/Summer Season")
win_rate = sum(1 for p in azir_stats if p.did_win) / len(azir_stats) * 100
# Analyze champion effectiveness across different players and tournaments

# Role performance comparison
mid_players = lp.get_role_performance_comparison("LCK/2024 Season/Summer Season", "Mid")
top_performer = max(mid_players, key=lambda p: p.kda_ratio or 0)
# Compare player performance within specific roles

# MVP candidate detection
mvp_candidates = lp.get_tournament_mvp_candidates("LCK/2024 Season/Summer Season", min_games=10)
# Identify top-performing players based on consistency and performance metrics

# 📋 Contract Management
# Get active contracts
active_contracts = lp.get_active_contracts()
# [Contract(player='Faker', team='T1', contract_end='2025-12-31'), ...]

# Check expiring contracts
expiring_soon = lp.get_expiring_contracts(days=90)
# Monitor contract renewals and potential free agents

# Player contract history
faker_contracts = lp.get_player_contracts("Faker")
# Track contract changes and team commitments
```

## 🎯 Common Use Cases

```python
# 📊 Performance Analysis & Fantasy Esports
# Track individual player performance and trends
faker_stats = lp.get_player_match_history("Faker", limit=10)
performance_trend = [game.performance_grade for game in faker_stats]
avg_kda = sum(game.kda_ratio for game in faker_stats if game.kda_ratio) / len(faker_stats)

# Identify MVP candidates for tournaments
mvps = lp.get_tournament_mvp_candidates("LCK/2024 Season/Summer Season")
top_mvp = mvps[0]  # Highest performing player
print(f"Tournament MVP: {top_mvp.player_name} - {top_mvp.kda_ratio:.1f} KDA")

# 🏆 Tournament & Team Analysis
standings = lp.get_tournament_standings("LCK/2024 Season/Summer Season")
top_team = standings[0].team
roster = lp.get_tournament_rosters(top_team, "LCK/2024 Season/Summer Season")

# Analyze team synergy and individual contributions
team_performance = lp.get_team_match_performance(top_team, limit=20)
team_avg_damage = sum(p.damage_to_champions for p in team_performance if p.damage_to_champions)

# 📋 Contract & Roster Management
# Monitor contract expirations for potential transfers
expiring_contracts = lp.get_expiring_contracts(days=180)
free_agents_soon = [c.player for c in expiring_contracts if c.team == "T1"]

# Track roster changes and team building
recent_moves = lp.get_recent_roster_changes(days=7)
team_additions = lp.get_roster_additions(team="T1")

# 🎮 Meta Analysis & Champion Research
# Analyze champion effectiveness across different skill levels
azir_performance = lp.get_champion_performance_stats("Azir")
azir_win_rate = sum(1 for p in azir_performance if p.did_win) / len(azir_performance)

# Compare role effectiveness
mid_players = lp.get_role_performance_comparison("LCK/2024 Season/Summer Season", "Mid")
support_players = lp.get_role_performance_comparison("LEC/2024 Season/Summer Season", "Support")

# Item meta analysis
marksmen = lp.get_champions_by_attributes("Marksman")
crit_items = lp.search_items_by_stat("Crit")
```

## 📋 Data Types

| Module | Returns | Key Properties |
|--------|---------|----------------|
| **Performance** | `ScoreboardPlayer` | kda_ratio, performance_grade, kill_participation, gold_share |
| **Contracts** | `Contract` | player, team, contract_end, is_active, days_until_expiry |
| **Games** | `Game`, `GameDetails` | teams, winner, date, picks_bans |
| **Teams** | `TeamPlayer`, `TeamAssets` | name, role, logo, thumbnail |
| **Players** | `PlayerInfo` | name, country, birth_date, status |
| **Tournaments** | `Dict` (rosters) | team, tournament, player, role |
| **Standings** | `Standing` | team, place, win_rate, total_games |
| **Champions** | `Champion` | name, attributes, is_ranged, attack_range |
| **Items** | `Item` | name, tier, provides_ad/ap, total_cost |
| **Roster Changes** | `RosterChange` | player, team, direction, is_addition |

## ⚡ Performance Considerations

**For optimal performance with large datasets:**

```python
# ✅ GOOD: Use filters and limits for responsive queries
faker_recent = lp.get_player_match_history("Faker", limit=10)
t1_lck = lp.get_team_match_performance("T1", tournament="LCK/2024 Season/Summer Season")
specific_game = lp.get_game_scoreboard("ESPORTSTMNT01_2024_LCK_Game123")

# ⚠️ SLOW: Large unbounded queries (10+ years of data)
# all_faker_games = lp.get_player_match_history("Faker")  # Takes minutes!
```

**Best Practices:**
- Always use `limit` for exploratory analysis
- Filter by `tournament` for recent data
- Use specific `game_id` for detailed match analysis
- Start with small queries then expand scope as needed

## 📚 More Information

- **Examples**: Comprehensive usage examples in the [`tests` folder](https://github.com/thomasbarrepitous/leaguepedia_parser/tree/master/tests)
- **Development**: See [CLAUDE.md](CLAUDE.md) for development commands and setup
- **Original**: Based on [mrtolkien/leaguepedia_parser](https://github.com/mrtolkien/leaguepedia_parser)
- **Rate Limits**: Leaguepedia API has rate limits - the library handles basic throttling

## 🤝 Contributing

This enhanced fork welcomes contributions! Areas of interest:
- Advanced analytics features (win prediction, meta trends)
- Additional Cargo table parsers (Pentakills, Bans, etc.)
- Performance optimizations for large datasets
- Enhanced visualization integrations
- Better error handling and retry logic
- Documentation improvements

**Major Features:**
- ✅ **ScoreboardPlayers** - Complete match statistics with performance analytics
- ✅ **Contracts** - Player contract tracking and management
- ✅ **Advanced Filtering** - Tournament, role, and time-based queries
- ✅ **Performance Grading** - Automated player performance assessment
