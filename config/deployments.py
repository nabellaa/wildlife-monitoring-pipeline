# to pick cameratrap folders before run to pipeline

# ==================================================
# Get Deployments
# ==================================================

from config.paths import SAMPLE_PATH, BATCH_SAMPLE_PATH

def get_deployments():
    """
    Return all top level deployment folders.
    - sample: reads from data/sample/
    - batch_sample: reads from data/batch_sample/
    """

    return sorted(
        folder.name
        for folder in BATCH_SAMPLE_PATH.iterdir()
        if folder.is_dir()
    )

# ==================================================
# Get Deployment Path
# ==================================================

def get_deployment_path(deployment):
    """
    Return the full path to a deployment folder.
    """

    return BATCH_SAMPLE_PATH / deployment

# ==================================================
# Discover Deployments
# ==================================================

def summarize_deployment(deployment):
    """
    Return a summary of a deployment folder.
    """
    deployment_path = get_deployment_path(deployment)

    images = discover_images(
        deployment_path
    )
    return {
        "deployment": deployment,
        "path": deployment_path,
        "images": images,
        "image_count": len(images)
    }

# ==================================================
# Discover Images
# ==================================================

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff"
)

def discover_images(deployment_path):
    """
    Recursively find all images inside a deployment.
    regardless of how nested the folder structure is.

    Supports:
        november/camera-name/photos/
        july/day1/camera-name/sd-card/
    """

    images = []

    for extension in IMAGE_EXTENSIONS:

        images.extend(
            deployment_path.rglob(f"*{extension}")
        )

        images.extend(
            deployment_path.rglob(f"*{extension.upper()}")
        )

    return sorted(set(images))