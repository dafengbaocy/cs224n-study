#!/usr/bin/env python3
from __future__ import annotations
import json, runpy, sys, traceback
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path

nb_path = Path(sys.argv[1])
nb = json.loads(nb_path.read_text())
ns = {"__name__": "__notebook_exec__"}
failed = False
for i, cell in enumerate(nb.get("cells", []), start=1):
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    out, err = StringIO(), StringIO()
    try:
        with redirect_stdout(out), redirect_stderr(err):
            exec(compile(src, f"{nb_path}::cell{i}", "exec"), ns)
    except SystemExit as exc:
        if exc.code not in (0, None):
            failed = True
            print(f"cell {i} SystemExit {exc.code}")
    except Exception:
        failed = True
        print(f"cell {i} raised exception")
        traceback.print_exc()
    print(f"cell {i} stdout_chars {len(out.getvalue())} stderr_chars {len(err.getvalue())}")
if failed:
    raise SystemExit(1)
print(f"notebook_executed_ok {nb_path}")
