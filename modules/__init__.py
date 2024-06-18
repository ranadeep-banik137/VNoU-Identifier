# modules/__init__.py
import logging
# You can import modules from the package
from .speech import *
from .data_cache import *
from .data_reader import *
from .data_transfer import *
from .database import *
from .date_time_converter import *
from .event_data_handler import *
from .exportdb import *
from .face_identifier import *
from .image_identifier import *
from .config_reader import *


# You can define any initialization code here if needed
# For example:
logging.info("Initializing the 'modules' package...")
