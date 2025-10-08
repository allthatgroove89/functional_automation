"""
Mapping between JSON objective IDs and their handler functions.
Import this mapping to resolve a JSON objective to code to run.
"""
from . import handlers


OBJECTIVE_HANDLERS = {
    'spotify_play': handlers.spotify_play,
    'spotify_pause': handlers.spotify_pause,
    'spotify_next_track': handlers.spotify_next_track,
    'spotify_previous_track': handlers.spotify_previous_track,
    # Add more mappings as handlers are implemented
}


def get_handler_for_objective_id(objective_id):
    return OBJECTIVE_HANDLERS.get(objective_id)
