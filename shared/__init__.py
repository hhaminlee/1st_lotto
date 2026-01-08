"""
Shared module for Lotto Number application.
Contains common logic used by both backend and Firebase functions.
"""

from .constants import *
from .lotto_api import get_lotto_win_numbers, get_latest_draw_number
from .analysis import analyze_number_frequency, get_recommended_numbers
from .weekly_stats import get_current_week, calculate_prize_rank, WeeklyStatsManager
from .firebase_client import get_firestore_client, initialize_firebase

__all__ = [
    # Constants
    "DHLOTTERY_BASE_URL",
    "DHLOTTERY_API_URL",
    "COLLECTION_LOTTO_HISTORY",
    "COLLECTION_WEEKLY_STATS",
    "COLLECTION_WEEKLY_HISTORY",
    "DRAW_DAY",
    "DRAW_HOUR",
    "DRAW_MINUTE",
    # Lotto API
    "get_lotto_win_numbers",
    "get_latest_draw_number",
    # Analysis
    "analyze_number_frequency",
    "get_recommended_numbers",
    # Weekly Stats
    "get_current_week",
    "calculate_prize_rank",
    "WeeklyStatsManager",
    # Firebase
    "get_firestore_client",
    "initialize_firebase",
]
