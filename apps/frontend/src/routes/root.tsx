import {
  Link,
  Outlet,
  isRouteErrorResponse,
  useLocation,
  useRouteError,
} from "react-router-dom";

/** 全ページ共通のレイアウト(ヘッダ + メイン)。 */
export function RootLayout() {
  const isFront = useLocation().pathname.startsWith("/front");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between gap-3 px-4 py-4">
          <Link
            to={isFront ? "/front" : "/"}
            className="text-lg font-bold tracking-tight"
          >
            HRS{" "}
            <span className="font-normal text-slate-500">
              {isFront ? "フロント" : "ホテル予約"}
            </span>
          </Link>
          {isFront ? (
            <Link
              to="/"
              className="text-sm text-slate-600 hover:text-slate-900"
            >
              利用者画面
            </Link>
          ) : (
            <nav className="flex items-center gap-4">
              <a
                href="/#rooms"
                className="text-sm text-slate-600 hover:text-slate-900"
              >
                部屋を探す
              </a>
              <Link
                to="/front"
                className="text-sm text-slate-600 hover:text-slate-900"
              >
                フロント係
              </Link>
            </nav>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}

/** ローダーが投げた Response やその他の例外を表示する。 */
export function ErrorPage() {
  const error = useRouteError();
  const isFront = useLocation().pathname.startsWith("/front");
  const message = isRouteErrorResponse(error)
    ? error.data || `${error.status} ${error.statusText}`
    : "予期しないエラーが発生しました";
  return (
    <div className="mx-auto max-w-4xl px-4 py-16 text-center">
      <h1 className="text-2xl font-bold">問題が発生しました</h1>
      <p className="mt-3 text-slate-600">{String(message)}</p>
      <Link
        to={isFront ? "/front" : "/"}
        className="mt-6 inline-block rounded-lg bg-slate-900 px-4 py-2 text-white hover:bg-slate-700"
      >
        {isFront ? "フロント係画面へ戻る" : "トップへ戻る"}
      </Link>
    </div>
  );
}
