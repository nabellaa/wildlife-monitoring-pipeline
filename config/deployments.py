# to pick cameratrap folders before run to pipeline

# ==================================================
# Deployment Helper
# ==================================================

from config.paths import SAMPLE_PATH


def get_deployments():
    """
    Return all deployment folders inside data/sample.
    """

    return sorted(
        folder.name
        for folder in SAMPLE_PATH.iterdir()
        if folder.is_dir()
    )


def get_deployment_path(deployment):
    return SAMPLE_PATH / deployment