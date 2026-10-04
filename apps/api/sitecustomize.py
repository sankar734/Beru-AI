import sys
from pathlib import Path

# Add project root to sys.path so 'apps' and 'services' are always discovered
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
