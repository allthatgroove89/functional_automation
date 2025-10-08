import os
import sys
import json

# Ensure project root on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import load_config, get_app_config
from workflow import WorkflowManager


def main():
    cfg = load_config()
    app_name = 'Spotify'
    app_cfg = get_app_config(cfg, app_name)

    wm = WorkflowManager(cfg)

    print('Executing spotify_test_basic objective...')
    ok = wm.execute_single_objective(app_name, app_cfg, 'spotify_test_basic')
    print('Result:', ok)

if __name__ == '__main__':
    main()
