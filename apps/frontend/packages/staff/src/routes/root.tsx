import { Link, Outlet, isRouteErrorResponse, useRouteError } from "react-router-dom";

/** フロント係アプリ共通のレイアウト(ヘッダ + メイン)。
利用者アプリとは別オリジンで配信する前提のため、利用者画面への導線は持たない。 */
export function RootLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between gap-3 px-4 py-4">
          <Link to="/" className="text-lg font-bold tracking-tight">
            HRS <span className="font-normal text-slate-500">フロント係</span>
          </Link>
          <span className="text-sm text-slate-500">ホテルスタッフ専用</span>
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
  const message = isRouteErrorResponse(error)
    ? error.data || `${error.status} ${error.statusText}`
    : "予期しないエラーが発生しました";
  return (
    <div className="mx-auto max-w-4xl px-4 py-16 text-center">
      <h1 className="text-2xl font-bold">問題が発生しました</h1>
      <p className="mt-3 text-slate-600">{String(message)}</p>
      <Link
        to="/"
        className="mt-6 inline-block rounded-lg bg-slate-900 px-4 py-2 text-white hover:bg-slate-700"
      >
        予約検索へ戻る
      </Link>
    </div>
  );
}
