import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // 利用者アプリ(5173)と別オリジンにする。cookie/localStorage/CSPの境界はオリジン単位のため、
  // パスではなくポート(本番ではホスト)を分けることが分離の前提になる。
  server: { port: 5174 },
});
