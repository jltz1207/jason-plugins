#!/usr/bin/env python3
"""Two-way sync of Claude Code session transcripts between WSL2 and Windows.

WSL stores sessions under ~/.claude/projects/-mnt-c-Users-me/<id>.jsonl,
Windows under %USERPROFILE%\\.claude\\projects\\C--Users-me\\<id>.jsonl.
This script copies each session to the other side, rewriting the "cwd"
field so /resume works there, and keeps the longer copy when both sides
have the same (append-only) session.

Dry-run by default; pass --apply to write. Standard library only; runs on
either WSL (python3) or Windows (python).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

IS_WINDOWS = os.name == "nt"
WSL_MNT = re.compile(r"^/mnt/([a-zA-Z])(/.*)?$")
WIN_DRIVE = re.compile(r"^([a-zA-Z]):(\\.*)?$")
CWD_FIELD = re.compile(r'"cwd":("(?:[^"\\]|\\.)*")')


# ---------- path conversion ----------

def wsl_to_win(p):
    m = WSL_MNT.match(p)
    if not m:
        return None
    rest = (m.group(2) or "/").replace("/", "\\")
    return f"{m.group(1).upper()}:{rest}"


def win_to_wsl(p):
    m = WIN_DRIVE.match(p)
    if not m:
        return None
    rest = (m.group(2) or "").replace("\\", "/").rstrip("/")
    return f"/mnt/{m.group(1).lower()}{rest}"


def encode_project_dir(cwd):
    """Claude Code's project dir naming: every non-alphanumeric char -> '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", cwd)


# ---------- roots ----------

def run(cmd):
    out = subprocess.run(cmd, capture_output=True, timeout=30)
    return out.stdout.decode("utf-8", "replace").replace("\0", "").strip()


def detect_roots(args):
    if IS_WINDOWS:
        win = Path(args.win_root or Path(os.environ["USERPROFILE"]) / ".claude")
        if args.wsl_root:
            wsl = Path(args.wsl_root)
        else:
            info = run(["wsl.exe", "-e", "sh", "-c", 'echo "$WSL_DISTRO_NAME"; echo "$HOME"']).splitlines()
            if len(info) < 2:
                sys.exit("Cannot detect WSL distro/home; pass --wsl-root")
            distro, home = info[0].strip(), info[1].strip()
            wsl = Path(rf"\\wsl.localhost\{distro}" + home.replace("/", "\\")) / ".claude"
    else:
        wsl = Path(args.wsl_root or Path.home() / ".claude")
        if args.win_root:
            win = Path(args.win_root)
        else:
            profile = run(["cmd.exe", "/c", "echo %USERPROFILE%"]).splitlines()[-1].strip()
            win = Path(run(["wslpath", "-u", profile])) / ".claude"
    for name, root in (("WSL", wsl), ("Windows", win)):
        if not (root / "projects").is_dir():
            sys.exit(f"{name} projects dir not found: {root / 'projects'}")
    return wsl, win


# ---------- transcript helpers ----------

def convert_text(text, conv):
    """Rewrite every "cwd" value in a JSONL text with conv(); keep unmappable ones."""
    def repl(m):
        try:
            old = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        new = conv(old)
        if new is None:
            return m.group(0)
        return '"cwd":' + json.dumps(new, ensure_ascii=False)
    return CWD_FIELD.sub(repl, text)


def first_cwd(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = CWD_FIELD.search(line)
            if m:
                try:
                    return json.loads(m.group(1))
                except ValueError:
                    continue
    return None


def read_text(path):
    with open(path, encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def atomic_write(path, text, mtime, private):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".sync-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    if private:
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    os.utime(path, (mtime, mtime))


def index_sessions(root):
    """session id -> path of <id>.jsonl, across all project dirs."""
    idx = {}
    for d in (root / "projects").iterdir():
        if not d.is_dir():
            continue
        for f in d.glob("*.jsonl"):
            idx[f.stem] = f
    return idx


def find_project_dir(root, name, case_insensitive):
    projects = root / "projects"
    if case_insensitive:
        # Windows may already have e.g. "c--Users-..." from a lowercase drive cwd.
        for d in projects.iterdir():
            if d.is_dir() and d.name.lower() == name.lower():
                return d
    return projects / name


# ---------- side model ----------

class Side:
    def __init__(self, name, root, to_canon, from_canon, private, ci):
        self.name = name
        self.root = root
        self.to_canon = to_canon      # this side's cwd -> canonical (WSL form)
        self.from_canon = from_canon  # canonical -> this side's cwd
        self.private = private        # chmod 600 written files
        self.ci = ci                  # project dir names case-insensitive
        self.idx = index_sessions(root)


def canon_text(side, path):
    text = read_text(path)
    return text if side.to_canon is None else convert_text(text, side.to_canon)


def local_text(side, canon):
    return canon if side.from_canon is None else convert_text(canon, side.from_canon)


def backup(side, target, stamp):
    rel = target.relative_to(side.root / "projects")
    dest = side.root / "backups" / "session-sync" / stamp / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if target.is_dir():
        shutil.copytree(target, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(target, dest)


def copy_session(src_side, src, dst_side, dst, stamp, apply):
    """Write src session (+ its <id>/ dir) onto dst path, converting cwd."""
    if not apply:
        return
    if dst.exists():
        backup(dst_side, dst, stamp)
    canon = canon_text(src_side, src)
    atomic_write(dst, local_text(dst_side, canon), src.stat().st_mtime, dst_side.private)
    src_dir, dst_dir = src.with_suffix(""), dst.with_suffix("")
    if not src_dir.is_dir():
        return
    for f in src_dir.rglob("*"):
        if not f.is_file():
            continue
        out = dst_dir / f.relative_to(src_dir)
        st = f.stat()
        if out.exists() and out.stat().st_size == st.st_size and out.stat().st_mtime >= st.st_mtime:
            continue
        if f.suffix == ".jsonl":
            atomic_write(out, local_text(dst_side, canon_text(src_side, f)), st.st_mtime, dst_side.private)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)
            if dst_side.private:
                try:
                    os.chmod(out, 0o600)
                except OSError:
                    pass


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    ap.add_argument("--include-active", action="store_true",
                    help="also sync sessions modified within --active-minutes")
    ap.add_argument("--active-minutes", type=float, default=5.0)
    ap.add_argument("--wsl-root", help="WSL ~/.claude path (as seen from this OS)")
    ap.add_argument("--win-root", help="Windows %%USERPROFILE%%\\.claude path (as seen from this OS)")
    ap.add_argument("-v", "--verbose", action="store_true", help="list every action")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    wsl_root, win_root = detect_roots(args)
    wsl = Side("WSL", wsl_root, None, None, private=True, ci=False)
    win = Side("Windows", win_root, win_to_wsl, wsl_to_win, private=False, ci=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    cutoff = time.time() - args.active_minutes * 60

    print(f"WSL root:     {wsl_root}")
    print(f"Windows root: {win_root}")
    print(f"Mode:         {'APPLY' if args.apply else 'DRY-RUN'}\n")

    counts = {k: 0 for k in ("to_win", "to_wsl", "upd_win", "upd_wsl", "same", "active",
                             "conflict", "unmappable", "empty")}
    conflicts, unmappable, actions = [], [], []

    for sid in sorted(set(wsl.idx) | set(win.idx)):
        a, b = wsl.idx.get(sid), win.idx.get(sid)
        if not args.include_active and any(p and p.stat().st_mtime > cutoff for p in (a, b)):
            counts["active"] += 1
            continue

        if a and b:
            ca, cb = canon_text(wsl, a), canon_text(win, b)
            if ca == cb:
                counts["same"] += 1
                continue
            if ca.startswith(cb):
                actions.append(f"update  WSL -> Windows  {sid}  ({b.parent.name})")
                copy_session(wsl, a, win, b, stamp, args.apply)
                counts["upd_win"] += 1
            elif cb.startswith(ca):
                actions.append(f"update  Windows -> WSL  {sid}  ({a.parent.name})")
                copy_session(win, b, wsl, a, stamp, args.apply)
                counts["upd_wsl"] += 1
            else:
                conflicts.append(f"{sid}  WSL:{a.parent.name}  Windows:{b.parent.name}")
                counts["conflict"] += 1
            continue

        src_side, src, dst_side = (wsl, a, win) if a else (win, b, wsl)
        cwd = first_cwd(src)
        if cwd is None:
            counts["empty"] += 1
            continue
        canon = cwd if src_side is wsl else win_to_wsl(cwd)
        target_cwd = canon if dst_side is wsl else (wsl_to_win(canon) if canon else None)
        if not target_cwd:
            unmappable.append(f"{src_side.name}  {sid}  cwd={cwd}")
            counts["unmappable"] += 1
            continue
        proj = find_project_dir(dst_side.root, encode_project_dir(target_cwd), dst_side.ci)
        dst = proj / src.name
        actions.append(f"copy    {src_side.name} -> {dst_side.name}  {sid}  ({proj.name})")
        copy_session(src_side, src, dst_side, dst, stamp, args.apply)
        counts["to_win" if dst_side is win else "to_wsl"] += 1

    if args.verbose:
        for line in actions:
            print(line)
        print()
    else:
        per_proj = {}
        for line in actions:
            key = line.split("(")[-1].rstrip(")") + "  [" + line.split()[1] + "->" + line.split()[3] + "]"
            per_proj[key] = per_proj.get(key, 0) + 1
        for key, n in sorted(per_proj.items()):
            print(f"{n:4d}  {key}")
        if per_proj:
            print()

    if conflicts:
        print("Conflicts (both sides diverged, left untouched):")
        for c in conflicts:
            print("  " + c)
        print()
    if unmappable:
        print("Unmappable (cwd not under /mnt/<drive> or <drive>:\\, skipped):")
        for u in unmappable[:20]:
            print("  " + u)
        if len(unmappable) > 20:
            print(f"  ... and {len(unmappable) - 20} more")
        print()

    print("Summary:")
    print(f"  copied  WSL -> Windows : {counts['to_win']}")
    print(f"  copied  Windows -> WSL : {counts['to_wsl']}")
    print(f"  updated Windows copy   : {counts['upd_win']}")
    print(f"  updated WSL copy       : {counts['upd_wsl']}")
    print(f"  already in sync        : {counts['same']}")
    print(f"  skipped (active)       : {counts['active']}")
    print(f"  conflict               : {counts['conflict']}")
    print(f"  unmappable             : {counts['unmappable']}")
    print(f"  no cwd (empty)         : {counts['empty']}")
    if not args.apply:
        print("\nDry-run only. Re-run with --apply to write.")
    elif any(counts[k] for k in ("upd_win", "upd_wsl")):
        print(f"\nOverwritten files backed up under backups/session-sync/{stamp}/ on the target side.")


if __name__ == "__main__":
    main()
