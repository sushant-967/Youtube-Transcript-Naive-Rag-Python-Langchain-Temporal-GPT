


import os


def use_temporal_ingestion() -> bool:
    return os.environ.get("USE_TEMPORAL_INGESTION", "false").lower() in ["true", "1", "yes","y"]