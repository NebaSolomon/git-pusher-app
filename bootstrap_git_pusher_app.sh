#!/usr/bin/env bash
set -euo pipefail

# ===== Config =====
WIN_TARGET_DEFAULT='C:\Users\LEGION\Desktop\productivity\created apps\git-pusher-app'
WIN_TARGET="${1:-$WIN_TARGET_DEFAULT}"

# Convert Windows path -> Unix for Git Bash
if command -v cygpath >/dev/null 2>&1; then
  TARGET_DIR="$(cygpath -u "$WIN_TARGET" 2>/dev/null || echo "$WIN_TARGET")"
else
  TARGET_DIR="$WIN_TARGET"
fi

echo "📦 Creating project at: $TARGET_DIR"
mkdir -p "$TARGET_DIR/base" "$TARGET_DIR/gui"

# ----- push_it.sh (core logic) -----
cat > "$TARGET_DIR/base/push_it.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

# Usage: push_it.sh <PROJECT_DIR> <VERSION> <REPO_URL> <BRANCH>
PROJECT_DIR="${1:-}"
VERSION="${2:-v1.0}"
REPO_URL="${3:-}"
BRANCH="${4:-main}"

die()  { echo "❌ $*" >&2; exit 1; }
ok()   { echo "✅ $*"; }
note() { echo "ℹ️  $*"; }
warn() { echo "⚠️  $*"; }

[[ -n "$PROJECT_DIR" ]] || die "Missing project folder"
[[ -n "$REPO_URL"    ]] || die "Missing repo URL (e.g. https://github.com/user/repo.git)"
[[ -n "$BRANCH"      ]] || die "Missing branch"

command -v git >/dev/null 2>&1 || die "git not found on PATH"

# Normalize Windows path to Unix for Git Bash
if command -v cygpath >/dev/null 2>&1; then
  PROJECT_DIR="$(cygpath -u "$PROJECT_DIR" 2>/dev/null || echo "$PROJECT_DIR")"
fi
[[ -d "$PROJECT_DIR" ]] || die "Directory not found: $PROJECT_DIR"
cd "$PROJECT_DIR"

echo "📂 Project:  $PROJECT_DIR"
echo "🏷  Version: $VERSION"
echo "🌐 Repo:     $REPO_URL"
echo "🌿 Branch:   $BRANCH"
echo

# Minimal ignore (first-time convenience)
if [[ ! -f .gitignore ]]; then
  cat > .gitignore <<'GITIGNORE'
build/
dist/
*.spec
*.exe
__pycache__/
*.pyc
*.log
.DS_Store
Thumbs.db
node_modules/
GITIGNORE
  ok ".gitignore created"
fi

# Init repo if missing
if [[ ! -d .git ]]; then
  git init
  ok "Initialized git repo"
fi

# Ensure branch exists/checked out
current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
if [[ "$current_branch" != "$BRANCH" ]]; then
  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    git checkout "$BRANCH"
  else
    git checkout -b "$BRANCH"
  fi
fi

# Set/Update remote
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
  note "Updated origin → $REPO_URL"
else
  git remote add origin "$REPO_URL"
  ok   "Added origin → $REPO_URL"
fi

# Sync with remote to avoid rejects
if git ls-remote --heads origin "$BRANCH" | grep -q .; then
  note "Syncing with origin/$BRANCH (rebase)"
  if ! git pull --rebase --autostash origin "$BRANCH"; then
    note "Rebase failed; retry merge (prefer local), allowing unrelated histories"
    git rebase --abort || true
    git fetch origin "$BRANCH" || true
    git merge -X ours --allow-unrelated-histories origin/"$BRANCH" \
      -m "Merge origin/$BRANCH (prefer local)"
  fi
else
  note "origin/$BRANCH does not exist yet (first push)."
fi

# Commit & push (always produce a visible version commit)
git add -A
git commit --allow-empty -m "UAEServiceHub (kuku) ${VERSION}" || true
ok "Commit recorded: UAEServiceHub (kuku) ${VERSION}"

git push -u origin "$BRANCH"
ok "Pushed branch '$BRANCH'"

# Tag handling
if git ls-remote --tags origin "refs/tags/$VERSION" | grep -q .; then
  warn "Tag '$VERSION' already exists on remote; skipping."
else
  if ! git show-ref --quiet --tags "refs/tags/$VERSION"; then
    git tag -a "$VERSION" -m "Release $VERSION"
    ok "Created tag '$VERSION'"
  fi
  git push origin "$VERSION"
  ok "Pushed tag '$VERSION'"
fi

echo
echo "🎉 Done: pushed '$PROJECT_DIR' → $REPO_URL ($BRANCH, $VERSION)"
SH
chmod +x "$TARGET_DIR/base/push_it.sh"

# ----- press_and_push.cmd (prompt runner) -----
cat > "$TARGET_DIR/base/press_and_push.cmd" <<'CMD'
@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Git Pusher App - Bash Backend

REM Path to Git Bash and script
set "BASH_EXE=C:\Program Files\Git\git-bash.exe"
set "SH=%~dp0push_it.sh"

if not exist "%BASH_EXE%" (
  echo [ERROR] Git Bash not found at "%BASH_EXE%".
  echo Install Git for Windows or fix the path.
  pause
  exit /b 1
)
if not exist "%SH%" (
  echo [ERROR] Missing push_it.sh at "%SH%".
  pause
  exit /b 1
)

REM Prompts
set /p "PROJECT_DIR=Drag or enter project folder: "
set /p "VERSION=Version tag [default v1.0]: "
if "%VERSION%"=="" set "VERSION=v1.0"
set /p "REPO_URL=Repo URL (https://github.com/user/repo.git): "
set /p "BRANCH=Branch [default main]: "
if "%BRANCH%"=="" set "BRANCH=main"

set "CHERE_INVOKING=1"
set "MSYS2_ARG_CONV_EXCL=*"

echo.
echo 📂 Project : %PROJECT_DIR%
echo 🏷  Version : %VERSION%
echo 🌐 Repo    : %REPO_URL%
echo 🌿 Branch  : %BRANCH%
echo.

"%BASH_EXE%" -c "/usr/bin/env bash \"$(cygpath -u '%SH%')\" \"$(cygpath -u '%PROJECT_DIR%')\" \"%VERSION%\" \"%REPO_URL%\" \"%BRANCH%\""
set "ERR=%ERRORLEVEL%"
echo.
if not "%ERR%"=="0" (
  echo [ERROR] push_it.sh exited with code %ERR%
) else (
  echo [OK] Completed successfully.
)
echo.
pause
exit /b %ERR%
CMD

# ----- Simple GUI (optional) -----
cat > "$TARGET_DIR/gui/main.py" <<'PY'
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess, os, shlex

def browse():
    folder = filedialog.askdirectory()
    if folder:
        project_var.set(folder)

def push():
    project = project_var.get().strip()
    version = version_var.get().strip() or "v1.0"
    repo    = repo_var.get().strip()
    branch  = branch_var.get().strip() or "main"

    if not project or not repo:
        messagebox.showerror("Error", "Please provide project folder and repo URL.")
        return

    bash = r"C:\Program Files\Git\git-bash.exe"
    sh   = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "base", "push_it.sh"))
    cmd  = [bash, "-c", f"bash {shlex.quote(sh)} {shlex.quote(project)} {shlex.quote(version)} {shlex.quote(repo)} {shlex.quote(branch)}"]

    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"Pushed to {repo} ({branch}, {version})")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Failed", f"Push failed.\n\n{e}")

root = tk.Tk()
root.title("Git Pusher App")
root.geometry("520x330")
root.resizable(False, False)

tk.Label(root, text="Project Folder:").pack(anchor="w", padx=20, pady=(15,5))
project_var = tk.StringVar()
tk.Entry(root, textvariable=project_var, width=60).pack(padx=20)
tk.Button(root, text="Browse", command=browse).pack(padx=20, pady=5)

tk.Label(root, text="Version (e.g. v1.0):").pack(anchor="w", padx=20)
version_var = tk.StringVar()
tk.Entry(root, textvariable=version_var, width=25).pack(padx=20, pady=4)

tk.Label(root, text="Repository URL:").pack(anchor="w", padx=20)
repo_var = tk.StringVar()
tk.Entry(root, textvariable=repo_var, width=60).pack(padx=20, pady=4)

tk.Label(root, text="Branch (default main):").pack(anchor="w", padx=20)
branch_var = tk.StringVar()
tk.Entry(root, textvariable=branch_var, width=25).pack(padx=20, pady=4)

tk.Button(root, text="🚀 Push to Git", width=20, command=push).pack(pady=16)

root.mainloop()
PY

# ----- requirements.txt -----
cat > "$TARGET_DIR/requirements.txt" <<'REQ'
# GUI uses the built-in tkinter from Python on Windows
# If you don't have it, install Python with Tcl/Tk support.
REQ

# ----- README.md -----
cat > "$TARGET_DIR/README.md" <<'MD'
# Git Pusher App

A tiny app to push **any folder** to **any repo/branch**:
- Drag/paste a folder
- Enter version, repo URL, branch
- One click to push + tag

## Backends
- **Bash**: `base/push_it.sh` (core logic)
- **Windows launcher**: `base/press_and_push.cmd`
- **GUI (optional)**: `gui/main.py` (Tkinter)

## Use
- **GUI**: `python gui/main.py`
- **CMD launcher**: double-click `base/press_and_push.cmd`
- **Direct Bash**: `bash base/push_it.sh "C:\path\to\project" v1.0 https://github.com/user/repo.git main`
MD

# ----- .gitignore -----
cat > "$TARGET_DIR/.gitignore" <<'IGN'
__pycache__/
*.pyc
.env
*.log
.vscode/
.idea/
IGN

# Make bash files executable (for Git Bash)
chmod +x "$TARGET_DIR/base/push_it.sh" || true

echo
echo "✅ All files created."
echo "➡ To run GUI:   python \"$TARGET_DIR/gui/main.py\""
echo "➡ To run CMD:   \"$TARGET_DIR/base/press_and_push.cmd\""
