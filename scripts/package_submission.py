from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "dist" / "WORMHOLE-submission.zip"
# An explicit manifest leaves repository history and local build files out.
SUBMISSION_FILES = (
    "README.md",
    "ACKNOWLEDGEMENTS.md",
    "ai_use.md",
    "game-requirements.md",
    "adapters.py",
    "adventure.py",
    "art.py",
    "klotski.py",
    "lights_out.py",
    "lights_out_game.py",
    "main.py",
    "minesweeper_game.py",
    "screens.py",
    "story.py",
    "scripts/package_submission.py",
    "tests/__init__.py",
    "tests/test_game.py",
)


def create_submission():
    missing = [
        name for name in SUBMISSION_FILES
        if not (PROJECT_ROOT / name).is_file()
    ]
    if missing:
        raise FileNotFoundError("Missing submission files: " + ", ".join(missing))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT_PATH, "w", compression=ZIP_DEFLATED) as archive:
        for name in SUBMISSION_FILES:
            archive.write(PROJECT_ROOT / name, arcname=name)
    return OUTPUT_PATH


if __name__ == "__main__":
    print("Created {}".format(create_submission()))
