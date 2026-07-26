#!/usr/bin/env bash
# docs/uml/*.puml から docs/uml/images/ にPNGを一括生成する。
# 出力ファイル名は @startuml に書かれた名前になるため、これを .puml のファイル名と
# 一致させる規約とし、下でその検査を行う(01_domain_class_diagram.puml →
# images/01_domain_class_diagram.png)。
# plantuml.jar は環境変数 PLANTUML_JAR で指定できる。
# 未指定の場合は VS Code の PlantUML 拡張(jebbs.plantuml)同梱のものを探す。
set -eu
cd "$(dirname "$0")"

# @startuml の名前が .puml のファイル名と一致していることを確認する。
mismatch=0
for puml in ./*.puml; do
  base="$(basename "$puml" .puml)"
  declared="$(awk '/^@startuml/ { print $2; exit }' "$puml")"
  if [ "$declared" != "$base" ]; then
    echo "$puml: @startuml の名前が '$declared' でファイル名 '$base' と一致しません" >&2
    mismatch=1
  fi
done
if [ "$mismatch" -ne 0 ]; then
  echo "生成される画像名がファイル名からずれるため中断します。" >&2
  exit 1
fi

JAR="${PLANTUML_JAR:-$(find ~/.vscode-server/extensions ~/.vscode/extensions \
  -name plantuml.jar -path '*jebbs*' 2>/dev/null | head -1)}"

if [ -z "$JAR" ]; then
  echo "plantuml.jar が見つかりません。環境変数 PLANTUML_JAR でパスを指定してください。" >&2
  exit 1
fi

java -jar "$JAR" -charset UTF-8 -tpng -o images ./*.puml
echo "generated $(ls images/*.png | wc -l) files -> $(pwd)/images/"
