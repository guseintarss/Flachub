#!/usr/bin/env bash
# Собирает статический демо-стенд и публикует его в GitHub Pages.
#
# По умолчанию используется специальный репозиторий пользовательского сайта
# guseintarss.github.io. Его содержимое полностью заменяется сборкой: не
# храните в нём ничего, кроме опубликованного стенда.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${DEMO_PAGES_REPO:-guseintarss/guseintarss.github.io}"
BRANCH="main"
BUILD_DIR="$ROOT/frontend/build"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

command -v gh >/dev/null || { echo "Нужен GitHub CLI (gh)." >&2; exit 1; }
command -v npm >/dev/null || { echo "Нужен npm." >&2; exit 1; }

echo "==> Сборка фронтенда с VITE_DEMO=true"
(
  cd "$ROOT/frontend"
  VITE_DEMO=true npm run build
)

if [ ! -f "$BUILD_DIR/index.html" ]; then
  echo "Сборка не создала index.html: $BUILD_DIR" >&2
  exit 1
fi

# GitHub Pages отдаёт 404.html для неизвестных путей. Копия index.html
# позволяет открывать /post/... и /profile/ по прямой ссылке.
cp "$BUILD_DIR/index.html" "$BUILD_DIR/404.html"
touch "$BUILD_DIR/.nojekyll"

echo "==> Подготовка репозитория $REPO"
if ! gh repo view "$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public \
    --description "ФлакХаб — интерактивный демо-стенд" >/dev/null
fi

if git ls-remote --exit-code --heads "https://github.com/$REPO.git" "$BRANCH" >/dev/null 2>&1; then
  git clone --depth=1 --branch "$BRANCH" "https://github.com/$REPO.git" "$WORK_DIR/site"
else
  mkdir -p "$WORK_DIR/site"
  git -C "$WORK_DIR/site" init -b "$BRANCH"
  git -C "$WORK_DIR/site" remote add origin "https://github.com/$REPO.git"
fi

# Оставляем только .git, чтобы удалённые из сборки файлы исчезли и на сайте.
find "$WORK_DIR/site" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -a "$BUILD_DIR"/. "$WORK_DIR/site"/

cd "$WORK_DIR/site"
git add -A
if git diff --cached --quiet; then
  echo "==> Изменений нет, публикация не нужна"
else
  git -c user.name="${GIT_AUTHOR_NAME:-Flachub Deploy}" \
      -c user.email="${GIT_AUTHOR_EMAIL:-deploy@flachub.local}" \
      commit -m "deploy: demo stand $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  git push origin "HEAD:$BRANCH"
fi

echo "==> Проверка GitHub Pages"
if ! gh api "repos/$REPO/pages" >/dev/null 2>&1; then
  printf '{"source":{"branch":"%s","path":"/"}}' "$BRANCH" \
    | gh api --method POST "repos/$REPO/pages" --input - >/dev/null
fi

OWNER="${REPO%%/*}"
NAME="${REPO##*/}"
if [ "$NAME" = "$OWNER.github.io" ]; then
  URL="https://$OWNER.github.io/"
else
  URL="https://$OWNER.github.io/$NAME/"
fi

echo
echo "Готово. GitHub Pages обновляется в течение минуты:"
echo "  $URL"
