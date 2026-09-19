import os
import pytest

# Force environment to testing during pytest execution
os.environ["ENVIRONMENT"] = "testing"

from app.config import get_settings
get_settings.cache_clear()
