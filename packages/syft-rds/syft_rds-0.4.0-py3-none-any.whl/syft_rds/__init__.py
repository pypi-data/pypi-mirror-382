__version__ = "0.4.0"

from syft_rds.utils.paths import RDS_NOTEBOOKS_PATH, RDS_REPO_PATH  # noqa
from syft_rds.display_utils.jupyter.display import display  # noqa
from syft_core import Client as SyftBoxClient  # noqa
from syft_rds.client.rds_client import RDSClient, init_session  # noqa
from syft_rds.client.setup import discover_rds_apps  # noqa
