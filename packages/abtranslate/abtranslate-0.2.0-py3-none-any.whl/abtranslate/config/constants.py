from pathlib import Path, PosixPath
import os

# Paths
PACKAGE_DIR = Path(f"/tmp/abtranslate/packages/")  # Use process ID for isolation

# Url's 
PACKAGES_INDEX = None

# Values
BATCH_SIZE = 32
DEFAULT_CT2_CONFIG = {  
                        "compute_type" : 'default', 
                        "inter_threads" : 1, 
                        "intra_threads" : 0,
                    }

DEFAULT_CT2_TRANSLATION_CONFIG = {   
                                    "beam_size": 2, 
                                    "patience": 1, 
                                    "num_hypotheses": 1, 
                                    "replace_unknowns": True, 
                                }

# ---------------------------------------------
# Regex:
# ---------------------------------------------
BOUNDARY = '||'
UNK_TOKEN = '$UNK'