# アーキテクチャ設計

パッケージ図: `10_package_diagram.puml`（画像: `images/package_diagram.png`）

## 1. 採用したアーキテクチャ

**多層アーキテクチャ（Layers architecture）** を採用した。システムを変更のしやすさごとに
層へ分割し、安定した層から順に積み上げる。

選択理由は、システム分析（08）で実施した BCE の識別結果がそのまま層に写るためである。
バウンダリ・コントロール・エンティティは「アクターとの入出力」「手順の制御」「業務ルールと
データ」という関心事で既に分離されているため、これを層の境界に採用すると、分析モデルと
実装の対応を追いやすく、かつ変更の影響範囲を層単位に閉じ込められる。

| 層 | BCE | 実装パッケージ | 責務 |
|---|---|---|---|
| ユーザインタフェース層 | バウンダリ | `apps/frontend`, `api.api`, `api.services` | アクターとの入出力、表現形式の変換、例外→HTTPステータス変換 |
| アプリケーション層 | コントロール | `libs.application` | ユースケース単位の手順制御、トランザクション境界 |
| ドメイン層 | エンティティ | `libs.domain` | 業務ルール（状態遷移の不変条件、料金計算）とデータ |
| データソース層 | — | `libs.infrastructure.db`, PostgreSQL | 永続化、接続管理 |

依存は上位層から下位層への一方向のみとし、下位層から上位層への依存は持たない。
ただしデータソース層は**ドメイン層に依存する**（`repositories` がドメインモデルを返す）。
これは古典的な多層アーキテクチャでドメイン層がデータソース層に依存する形とは逆向きで、
依存性を逆転させることでドメイン層をどの層にも依存しない最も安定した層に保っている。

## 2. 非機能要求との対応

| 非機能要求 | 実現手段 | 根拠・確認方法 |
|---|---|---|
| **開発の容易性**（アーキテクチャ設計後、異なるグループによる独立した開発が可能であること） | monorepo を `apps/frontend` と `apps/backend` に分割。バックエンドは uv workspace で `packages/api`（UI層）と `packages/libs`（アプリケーション層以下）に分割。フロント／バック間の契約は **OpenAPI に固定**し、`openapi-typescript` でフロントの型を生成する | 手書きのAPI型を持たないため、片側の契約変更が他方の**ビルドエラーとして検出**される。実際にフロントエンドとバックエンドは別々のPR（#7, #8）で並行開発した |
| **保守性**（UIの変更も含め、要求仕様の変更に対応しやすいこと） | 依存を上位→下位の一方向に限定し、業務ルールをドメイン層に集約。UIの変更はUI層に閉じる | 提供された部分実装のテキストUIから React SPA へ置き換えたが、`libs.application` / `libs.domain` は無変更。保守課題（UC5）の追加でも既存UCのコード変更は不要だった（第6節） |
| **性能効率性**（高性能である必要はない） | `Engine` をプロセス内で共有してコネクションプールを利用（`lru_cache`）。行ロック（`FOR UPDATE`）は競合が起こりうる空室確保と状態更新のみに限定 | 過度な最適化（キャッシュ層、非同期化）は行わず、単純さを優先した |
| **プラットフォーム**（Java言語・JavaVM環境、または他言語） | Python 3.13 + FastAPI | 「または他言語」の許容に基づく。型注釈と **mypy strict** による静的検査で、Javaの静的型付けに相当する検査水準を維持している |
| **永続性とネットワーク**（MySQLほか） | PostgreSQL。スキーマは `sqlc/schema.sql` を単一の正とし psqldef で適用。クエリは **sqlc** で型付きコードを生成。通信は HTTP/JSON | スキーマ適用の冪等性をCIで検証している（`schema-idempotency` ジョブ） |
| **UI**（テキストベースのUI、標準入出力が基本、発展形も可） | 発展形として React SPA（Vite + React Router + Tailwind） | 「発展形も可」に基づく。UI層の差し替えが下位層に影響しないことの実証にもなっている |
| **再利用可能な資産** | FastAPI, SQLAlchemy, Pydantic, sqlc, psqldef | 標準的なライブラリ・ツールを利用し、独自実装を最小化した |

## 3. 設計の基本概念の適用

| 基本概念 | 適用箇所 |
|---|---|
| 抽象化 | `repositories` が sqlc生成コードをドメインモデルへ変換する（データ抽象化）。`libs.application` の各 Control がユースケースの手順に名前を付ける（手続き抽象化） |
| モジュール化 | 層 → パッケージ → モジュールの3段で分解。ユースケース単位でモジュールを分けた |
| 関心事の分離 | BCE による分離をそのまま層に対応づけた |
| 情報隠蔽 | ドメイン層はテーブルのカラム構造を知らない。`gen`（sqlc生成コード）は `repositories` の外へ漏れない。`DbSettings` が接続情報の取得元（環境変数）を隠蔽する |
| 機能独立性 | 高凝集: Control はユースケース1つ分の手順のみを持つ。低結合: 層をまたぐ受け渡しはドメインモデルに限り、UI層はDBの語彙を知らない |

## 4. パッケージ設計原則の充足状況

| 原則 | 充足 | 説明 |
|---|---|---|
| 再利用・リリース等価の原則（REP） | ○ | `libs` はバージョンと `py.typed` を持つ独立パッケージとしてリリース可能。CLI等の別UIから再利用できる |
| 全再利用の原則（CRP） | △ | `libs.domain` / `libs.application` は API から一括して利用される。ただし `catalog`（部屋タイプ閲覧）は閲覧用途のみで、利用者によっては不要な部分を含む |
| 閉鎖性共通の原則（CCP） | △ | 業務ルールの変更理由はドメイン層に閉じる。一方でユースケースの追加は `api.api` と `libs.application` の2パッケージに及ぶ。これは層による責務分離とのトレードオフとして受け入れた |
| 非循環依存関係の原則（ADP） | ○ | パッケージ間に循環はない。`libs.domain` は他のどのパッケージも import しない |
| 安定依存の原則（SDP） | ○ | 依存は常により安定な方向（`api` → `application` → `domain`）へ向く。最も変更頻度が高いUI層が最も不安定な位置にある |
| 安定度・抽象度等価の原則（SAP） | △ | ドメイン層は最も安定だが、実装は具象 dataclass 中心で抽象度は高くない。Repository を `Protocol` として抽象化すれば、SAP と依存性逆転をより明確に満たせる（今後の課題） |

## 5. 分析モデル（09）との対応

| 09 のクラス | 実装 |
|---|---|
| boundary（画面側） | 下の表で個別に対応づける |
| boundary（API側） | `api.api.reservations` / `api.api.room_types` の route |
| `ReservationControl` 他の control | `libs.application.reservation` 他（クラス名を一致させている） |
| `Reservation` / `Guest` / `Room` entity | `libs.domain.reservation` |
| `RoomRate` / `ServiceUsage` / `Charge` entity | `libs.domain.billing` |
| `Reservation.チェックインする()` 等の操作 | `Reservation.check_in()` 等（状態遷移の可否判定を含む） |

### バウンダリ（画面）とフロントエンド実装の対応

08 のバウンダリ識別方針「アクター×ユースケースの組ごとに1つ」に合わせ、
`apps/frontend` を pnpm workspace とし、アクターごとに配信単位（オリジン）を分けている。

| 09 の boundary | アクター | 実装 |
|---|---|---|
| `ReservationUI` | 利用者 | `packages/guest/src/routes/roomType.tsx`（予約フォーム）<br>`packages/guest/src/routes/reservationComplete.tsx`（予約番号の提示） |
| `InquiryUI` | 利用者 | `packages/guest/src/routes/reservation.tsx` |
| `InquiryUI` | フロント係 | `packages/staff/src/routes/reservation.tsx` |
| `CancellationUI` | 利用者 | `packages/guest/src/routes/reservation.tsx` |
| `CheckInUI` | フロント係 | `packages/staff/src/routes/reservation.tsx` |
| `CheckOutUI` | フロント係 | `packages/staff/src/routes/reservation.tsx` |

上の表で `InquiryUI` の行が2つあるのは、09 のクラスが2つあるからではない。UC4 は
アクターが利用者・フロント係の2者であるため、08 の識別方針によりバウンダリ
**オブジェクト**が2つになる。提示する予約内容は同一なので 09 では1クラスに集約しており、
実装でもその表示部分を `packages/ui` の `ReservationSummary` として共有し、各アプリが
自分の画面に配置している。つまり「09のクラス1つ ＝ 分析上のオブジェクト2つ ＝
実装ファイル2つ ＋ 共有部品1つ」という対応になる。`packages/api-client` は OpenAPI から生成した型と HTTP クライアントで、
09 のクラスには対応しない実装上の共有部品である。

**同一ファイルに複数の boundary が同居している箇所がある。** `guest` の
`reservation.tsx` が `InquiryUI` と `CancellationUI` を、`staff` の `reservation.tsx` が
`InquiryUI` と `CheckInUI` と `CheckOutUI` を兼ねている。予約1件に対する参照と操作を
1画面で完結させる画面設計を優先した結果であり、ファイル分割で 09 と 1 対 1 に
できるが未対応である。

また、部屋タイプ閲覧（`packages/guest/src/routes/home.tsx`、`GET /room-types`、
`libs.application.catalog`）と、フロント係の予約番号検索
（`packages/staff/src/routes/home.tsx`）に対応するクラスは 09 に存在しない。
09 は UC1〜UC5 のみを対象としており、閲覧・検索の入口は分析工程で
ユースケースとして立てていないためである。

分析時点では技術非依存としていた事項のうち、**トランザクション境界**（アプリケーション層に
置く）と**行ロック**（`FOR UPDATE`）はこの設計工程で決定した。UC1 の例外フロー「予約登録の
直前に他の予約と競合した場合」が、空室行のロックによって実現されている。

## 6. 保守: UC5「予約をキャンセルする」の追加とその影響

保守課題として要求「顧客が予約をキャンセルする」を追加した。差分は以下のとおり。

| 工程 | 差分 |
|---|---|
| 要求分析 | UC5 をユースケース図に追加。UC4 を `<<include>>` して予約確認を再利用。ユースケース記述に代替フロー（キャンセル取りやめ）と例外フロー（キャンセル不可状態）を追加 |
| ドメイン分析 | 予約の状態に `CANCELLED` を追加 |
| システム分析 | `CancellationUI` / `CancellationControl` を追加。コラボレーション図 08e を追加。`Reservation.キャンセルする()`、`Room.空室に戻す()` を09に追加 |
| 実装 | `libs/application/cancellation.py`、`Reservation.cancel()`、route 1本（`POST /reservations/{id}/cancellation`）を追加 |

**影響の分析**

- **既存コードの変更が不要だった。** 追加されたのは新規モジュールと route のみで、UC1〜UC4 の
  コードは変更していない。これはユースケース単位でコントロールを分けた（高凝集）ことと、
  各層が下位層のインタフェースだけに依存していることによる。開放閉鎖原則に沿った拡張である。
- **状態遷移の判定をエンティティに置いた設計が効いた。** 「キャンセルできるのは予約済みのみ」
  という業務ルールは `Reservation.cancel()` の中にあり、コントロールやUI層に散らばっていない。
  そのため UC5 の例外フロー（キャンセル不可）は、既存の `InvalidReservationState` を
  UI層でHTTPステータスへ変換する既存の仕組みにそのまま乗った。
- **UC4 の再利用は分析レベルでは include、実装レベルでは分離した。** `CancellationControl` は
  `InquiryControl` を呼ばず、自身のトランザクション内で予約をロックして取得する。
  分析上の「予約内容の確認」と、実装上の「更新前提のロック付き取得」は目的が異なるためである。
  この差異はコラボレーション図（08e）とコードの対応を追うときの注意点になる。
- **残る影響として、キャンセルは客室状態を空室へ戻すため UC1 の空室検索と競合しうる。** 現状は
  予約行と客室行のロックで直列化している。より並行性を上げるならロック範囲の見直しが必要だが、
  性能効率性の要求が「高性能である必要はない」ため今回は単純な方式を選んだ。
