"""smoke test to ensure the project structure is intact"""
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parent.parent
def test_folders_exist():
    critical_paths=[
        "src/dpdp_auditor",
        "tests",
        "data/raw",
    ]
    for path in critical_paths:
        full_path=PROJECT_ROOT/path
        if not full_path.exists():
            print(f"❌ FAIL: Missing {path}")
            return False
        print(f"✅ OK: {path} exists")
    return True
if __name__=="__main__":
    print("Running smoke test...")
    if test_folders_exist():
        print("Smoke test passed!")
    else:
        print("Smoke test failed.")
