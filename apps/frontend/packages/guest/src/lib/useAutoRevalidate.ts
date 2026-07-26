import { useEffect } from "react";
import { useRevalidator } from "react-router-dom";

export function useAutoRevalidate(intervalMs = 3000) {
  const revalidator = useRevalidator();

  useEffect(() => {
    const refresh = () => {
      if (document.visibilityState === "visible" && revalidator.state === "idle") {
        revalidator.revalidate();
      }
    };

    const intervalId = window.setInterval(refresh, intervalMs);
    window.addEventListener("focus", refresh);
    return () => {
      window.clearInterval(intervalId);
      window.removeEventListener("focus", refresh);
    };
  }, [intervalMs, revalidator]);
}
