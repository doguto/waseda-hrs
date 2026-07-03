#!/usr/bin/env bash
# docs/uml/*.puml から docs/uml/images/ にPNGを一括生成する。
# plantuml.jar は環境変数 PLANTUML_JAR で指定できる。
# 未指定の場合は VS Code の PlantUML 拡張(jebbs.plantuml)同梱のものを探す。
set -eu
cd "$(dirname "$0")"

JAR="${PLANTUML_JAR:-$(find ~/.vscode-server/extensions ~/.vscode/extensions \
  -name plantuml.jar -path '*jebbs*' 2>/dev/null | head -1)}"

if [ -z "$JAR" ]; then
  echo "plantuml.jar が見つかりません。環境変数 PLANTUML_JAR でパスを指定してください。" >&2
  exit 1
fi

java -jar "$JAR" -charset UTF-8 -tpng -o images ./*.puml
echo "generated $(ls images/*.png | wc -l) files -> $(pwd)/images/"
