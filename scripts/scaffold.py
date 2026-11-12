"""Create the project folder structure."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DIRS = [
    "data/raw",
    "data/processed",
    "src/dpdp_auditor",
    "src/dpdp_auditor/ingestion",
    "src/dpdp_auditor/retrieval",
    "src/dpdp_auditor/agent",
    "src/dpdp_auditor/models",
    "src/dpdp_auditor/evaluation",
    "src/dpdp_auditor/api",
    "tests",
    "tests/fixtures",
    "scripts",
]

# Packages that need __init__.py
PACKAGES = [
    "src/dpdp_auditor",
    "src/dpdp_auditor/ingestion",
    "src/dpdp_auditor/retrieval",
    "src/dpdp_auditor/agent",
    "src/dpdp_auditor/models",
    "src/dpdp_auditor/evaluation",
    "src/dpdp_auditor/api",
    "tests",
]

def main() -> None:
    for d in DIRS:
        # TODO: create folder (parents=True, exist_ok=True)
        path=PROJECT_ROOT/d
        path.mkdir(parents=True,exist_ok=True)
    for pkg in PACKAGES:
        # TODO: touch __init__.py inside
        init_file=PROJECT_ROOT/pkg/"__init__.py"
        init_file.touch(exist_ok=True)
    print("scaffold complete")
if __name__ == "__main__":
    main()