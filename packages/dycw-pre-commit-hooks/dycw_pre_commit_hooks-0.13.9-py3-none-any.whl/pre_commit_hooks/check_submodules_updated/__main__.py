from __future__ import annotations

from pre_commit_hooks.check_submodules_updated import main

if __name__ == "__main__":
    raise SystemExit(int(not main()))
