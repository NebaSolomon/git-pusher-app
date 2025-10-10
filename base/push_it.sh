#!/usr/bin/env bash
set -euo pipefail
# Usage: push_it.sh <PROJECT_DIR> <VERSION> <REPO_URL> <BRANCH>
PROJECT_DIR="${1:-}"; VERSION="${2:-v1.0}"; REPO_URL="${3:-}"; BRANCH="${4:-main}"
die(){ echo "❌ $*" >&2; exit 1; }; ok(){ echo "✅ $*"; }; note(){ echo "ℹ️  $*"; }
[[ -n "$PROJECT_DIR" ]] || die "Missing project folder"
[[ -n "$REPO_URL"    ]] || die "Missing repo URL (e.g. https://github.com/user/repo.git)"
[[ -n "$BRANCH"      ]] || die "Missing branch"
command -v git >/dev/null 2>&1 || die "git not found"
if command -v cygpath >/dev/null 2>&1; then PROJECT_DIR="$(cygpath -u "$PROJECT_DIR" 2>/dev/null || echo "$PROJECT_DIR")"; fi
[[ -d "$PROJECT_DIR" ]] || die "Directory not found: $PROJECT_DIR"
cd "$PROJECT_DIR"
echo "📂 Project: $PROJECT_DIR"; echo "🏷  Version: $VERSION"; echo "🌐 Repo: $REPO_URL"; echo "🌿 Branch: $BRANCH"; echo
if [[ ! -f .gitignore ]]; then cat > .gitignore <<'GITIGNORE'
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
  ok ".gitignore created"; fi
if [[ ! -d .git ]]; then git init; ok "Initialized git repo"; fi
curr="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
if [[ "$curr" != "$BRANCH" ]]; then
  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then git checkout "$BRANCH"; else git checkout -b "$BRANCH"; fi
fi
if git remote get-url origin >/dev/null 2>&1; then git remote set-url origin "$REPO_URL"; note "Updated origin → $REPO_URL"; else git remote add origin "$REPO_URL"; ok "Added origin → $REPO_URL"; fi
if git ls-remote --heads origin "$BRANCH" | grep -q .; then
  note "Syncing with origin/$BRANCH (rebase)"
  if ! git pull --rebase --autostash origin "$BRANCH"; then
    note "Rebase failed; retry merge (prefer local), allowing unrelated histories"
    git rebase --abort || true
    git fetch origin "$BRANCH" || true
    git merge -X ours --allow-unrelated-histories origin/"$BRANCH" -m "Merge origin/$BRANCH (prefer local)"
  fi
else
  note "origin/$BRANCH does not exist yet (first push)."
fi
git add -A
git commit --allow-empty -m "UAEServiceHub (kuku) ${VERSION}" || true
ok "Commit recorded: UAEServiceHub (kuku) ${VERSION}"
git push -u origin "$BRANCH"
ok "Pushed branch '$BRANCH'"
if git ls-remote --tags origin "refs/tags/$VERSION" | grep -q .; then
  note "Tag '$VERSION' exists on remote; skipping."
else
  if ! git show-ref --quiet --tags "refs/tags/$VERSION"; then git tag -a "$VERSION" -m "Release $VERSION"; ok "Created tag '$VERSION'"; fi
  git push origin "$VERSION"; ok "Pushed tag '$VERSION'"
fi
echo; echo "🎉 Done: pushed '$PROJECT_DIR' → $REPO_URL ($BRANCH, $VERSION)"
