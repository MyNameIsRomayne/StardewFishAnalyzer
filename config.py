

import os
from utils import Path, read_file_json, ensure_file_exists

# If false, every object will load what is subjectively irrelevant for this code. 
# This is stuff like ignoring sale in random shops, sprite ID, etc.
# This reduces file size / ever so slightly increases load speed
IGNORE_IRRELEVANT_JSON = True