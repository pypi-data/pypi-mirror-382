"""
Entity package initialization
"""

from .fish import add_fish, add_all_fish
from .environment import add_environment, add_castle, add_seaweed, add_all_seaweed
from .special import add_shark, add_whale, add_ship, add_monster, add_big_fish, random_object

__all__ = [
    'add_fish',
    'add_all_fish',
    'add_environment',
    'add_castle',
    'add_seaweed',
    'add_all_seaweed',
    'add_shark',
    'add_whale',
    'add_ship',
    'add_monster',
    'add_big_fish',
    'random_object',
]
