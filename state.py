import os
import json
from datetime import datetime


def save_checkpoint(session_id, objective_id, action_index, history):
    """Save checkpoint to file"""
    checkpoint = {
        'session_id': session_id,
        'objective_id': objective_id,
        'action_index': action_index,
        'history': history,
        'timestamp': datetime.now().isoformat()
    }
    
    os.makedirs('checkpoints', exist_ok=True)
    with open(f'checkpoints/{session_id}.json', 'w') as f:
        json.dump(checkpoint, f, indent=2)


def load_checkpoint(session_id):
    """Load checkpoint from file"""
    path = f'checkpoints/{session_id}.json'
    if not os.path.exists(path):
        return None
    
    with open(path, 'r') as f:
        return json.load(f)


def append_to_history(history, action, status):
    """Add action to history list"""
    history.append({
        'action': action,
        'status': status,
        'timestamp': datetime.now().isoformat()
    })
    return history

