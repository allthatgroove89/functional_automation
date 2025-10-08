import json
import traceback
import os
import sys

# Ensure project root is on sys.path so imports like `window_ops` resolve when running tests
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from window_ops import find_window


def main():
    try:
        w = find_window('Spotify')
        if not w:
            print('NOT FOUND')
            return
        print('FOUND')
        info = {}
        for a in ['title', 'left', 'top', 'width', 'height', '_hWnd', 'hWnd']:
            try:
                info[a] = getattr(w, a)
            except Exception:
                info[a] = None
        print(json.dumps(info, default=str, indent=2))
    except Exception as e:
        print('ERROR running test:')
        traceback.print_exc()

if __name__ == '__main__':
    main()
