import { type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

export function HomePage() {
  const navigate = useNavigate();
  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const id = new FormData(event.currentTarget).get("id");
    const reservationId = String(id ?? "").trim();
    if (reservationId) navigate(`/reservations/${reservationId}`);
  };

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <header>
        <p className="text-sm font-medium text-slate-500">ホテルスタッフ専用</p>
        <h1 className="mt-1 text-2xl font-bold">フロント係画面</h1>
      </header>

      <section className="border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">予約を検索</h2>
        <p className="mt-1 text-sm text-slate-500">
          利用者から提示された予約番号を入力してください。
        </p>
        <form onSubmit={onSubmit} className="mt-5">
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">
              予約番号
            </span>
            <input
              name="id"
              required
              autoComplete="off"
              placeholder="例: 51aebfb3-9c8d-..."
              className="w-full border border-slate-300 px-3 py-2 shadow-sm outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
            />
          </label>
          <button
            type="submit"
            className="mt-4 w-full bg-slate-900 px-4 py-2.5 font-medium text-white hover:bg-slate-700"
          >
            予約内容を確認
          </button>
        </form>
      </section>
    </div>
  );
}
