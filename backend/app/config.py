import os


MIN_CONTOUR_AREA: int = int(os.environ.get("MIN_CONTOUR_AREA", "100"))
DEFAULT_K_CLUSTERS: int = int(os.environ.get("DEFAULT_K_CLUSTERS", "8"))
ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
