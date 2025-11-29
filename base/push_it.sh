#!/usr/bin/env bash
set -euo pipefail
# Usage: push_it.sh <PROJECT_DIR> <VERSION> <REPO_URL> <BRANCH> [COMMIT_MSG] [WHATS_NEW]

PROJECT_DIR="${1:-}"
VERSION="${2:-v1.0}"
REPO_URL="${3:-}"
BRANCH="${4:-main}"
COMMIT_MSG="${5:-${COMMIT_MSG:-}}"
WHATS_NEW_IN="${6:-${WHATS_NEW:-}}"

die(){ echo "❌ $*" >&2; exit 1; }
ok(){ echo "✅ $*"; }
note(){ echo "ℹ️  $*"; }

[[ -n "$PROJECT_DIR" ]] || die "Missing project folder"
[[ -n "$REPO_URL"    ]] || die "Missing repo URL (e.g. https://github.com/user/repo.git)"
[[ -n "$BRANCH"      ]] || die "Missing branch"

# Defaults
[[ -z "${COMMIT_MSG}" ]] && COMMIT_MSG="Git Pusher ${VERSION}"

command -v git >/dev/null 2>&1 || die "git not found"
if command -v cygpath >/dev/null 2>&1; then
  PROJECT_DIR="$(cygpath -u "$PROJECT_DIR" 2>/dev/null || echo "$PROJECT_DIR")"
fi
[[ -d "$PROJECT_DIR" ]] || die "Directory not found: $PROJECT_DIR"
cd "$PROJECT_DIR"

echo "📂 Project: $PROJECT_DIR"
echo "🏷  Version: $VERSION"
echo "📝 Commit : $COMMIT_MSG"
echo "🌐 Repo:    $REPO_URL"
echo "🌿 Branch:  $BRANCH"
echo

# ---- WHATS_NEW.txt (append verbatim if provided) ----
NOTEFILE="WHATS_NEW.txt"
if [[ -n "${WHATS_NEW_IN}" ]]; then
  {
    echo "==============================="
    echo "Version: $VERSION"
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Commit: $COMMIT_MSG"
    echo "-------------------------------"
    echo "What's new:"
    printf '%s\n' "$WHATS_NEW_IN"
    echo
  } >> "$NOTEFILE"
  ok "Updated $NOTEFILE"
else
  note "No what's-new text provided (skipping $NOTEFILE update)"
fi

# ---- Git setup ----
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

if [[ ! -d .git ]]; then
  git init
  ok "Initialized git repo"
fi

curr="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
if [[ "$curr" != "$BRANCH" ]]; then
  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    git checkout "$BRANCH"
  else
    git checkout -b "$BRANCH"
  fi
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
  note "Updated origin → $REPO_URL"
else
  git remote add origin "$REPO_URL"
  ok "Added origin → $REPO_URL"
fi

# ---- Sync with Remote ----
if git ls-remote --heads origin "$BRANCH" | grep -q .; then
  note "Syncing with origin/$BRANCH"
  
  # Fetch latest changes
  git fetch origin "$BRANCH"
  
  # Check if branches have diverged
  LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "")
  REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null || echo "")
  BASE=$(git merge-base HEAD "origin/$BRANCH" 2>/dev/null || echo "")
  
  if [ -z "$LOCAL" ] || [ -z "$REMOTE" ]; then
    note "Cannot determine branch state, attempting safe merge..."
    if ! git merge --no-ff "origin/$BRANCH" -m "Merge origin/$BRANCH"; then
      die "Merge conflict detected. Please resolve conflicts manually before pushing."
    fi
  elif [ "$LOCAL" = "$REMOTE" ]; then
    note "Already up to date with origin/$BRANCH"
  elif [ "$LOCAL" = "$BASE" ]; then
    note "Local branch is behind, fast-forwarding..."
    if ! git merge --ff-only "origin/$BRANCH"; then
      die "Fast-forward failed. Please pull manually."
    fi
  elif [ "$REMOTE" = "$BASE" ]; then
    note "Local branch is ahead, will push changes"
  else
    # Branches have diverged - require safe merge
    note "⚠️  WARNING: Branches have diverged!"
    LOCAL_COUNT=$(git rev-list --count HEAD ^origin/$BRANCH 2>/dev/null || echo "?")
    REMOTE_COUNT=$(git rev-list --count origin/$BRANCH ^HEAD 2>/dev/null || echo "?")
    note "Local commits ahead: $LOCAL_COUNT"
    note "Remote commits ahead: $REMOTE_COUNT"
    note "Attempting safe merge (will fail if conflicts exist)..."
    
    # Try merge without force strategies
    if ! git merge --no-ff "origin/$BRANCH" -m "Merge origin/$BRANCH"; then
      die "Merge conflict detected. Please resolve conflicts manually before pushing."
    fi
  fi
else
  note "origin/$BRANCH does not exist yet (first push)."
fi

# ---- Commit & Push ----
git add -A
git commit --allow-empty -m "$COMMIT_MSG" || true
ok "Commit recorded: $COMMIT_MSG"

git push -u origin "$BRANCH"
ok "Pushed branch '$BRANCH'"

# ---- Tag ----
if git ls-remote --tags origin "refs/tags/$VERSION" | grep -q .; then
  note "Tag '$VERSION' exists on remote; skipping."
else
  if ! git show-ref --quiet --tags "refs/tags/$VERSION" ; then
    git tag -a "$VERSION" -m "Release $VERSION"
    ok "Created tag '$VERSION'"
  fi
  git push origin "$VERSION"
  ok "Pushed tag '$VERSION'"
fi

echo
echo "🎉 Done: pushed '$PROJECT_DIR' → $REPO_URL ($BRANCH, $VERSION)"
[[ -f "$NOTEFILE" ]] && echo "📄 What's New noted in $NOTEFILE"
