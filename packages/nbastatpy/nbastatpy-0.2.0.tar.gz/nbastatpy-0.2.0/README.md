# NBAStatPy

[![PyPI version](https://badge.fury.io/py/nbastatpy.svg)](https://badge.fury.io/py/nbastatpy)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/aberghammer-analytics/NBAStatPy/workflows/Run%20Pytest/badge.svg)](https://github.com/aberghammer-analytics/NBAStatPy/actions)

## Overview

A simple, easy-to-use wrapper for the `nba_api` package to access NBA data for players, games, teams, and seasons.

## Quick Start

```python
from nbastatpy.player import Player

# Create a player object
player = Player("Giannis", season="2023", playoffs=True)

# Get data
awards = player.get_awards()
stats = player.get_career_stats()
```

## Main Classes

- **Player** - Access player stats, career data, and awards
- **Game** - Get boxscores, play-by-play, and game details
- **Season** - Query league-wide stats, lineups, and tracking data
- **Team** - Retrieve team rosters, stats, and splits


### Standalone Usage

```python
from nbastatpy.standardize import standardize_dataframe

df = standardize_dataframe(df, data_type='player')
```

## Installation

### Pip
```bash
pip install nbastatpy
```

### UV
```bash
uv add nbastatpy
```
