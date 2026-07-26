const STORAGE_KEY = "hrs-reservation-ids";

function readReservationIds(): string[] {
  if (typeof window === "undefined") return [];

  try {
    const value = JSON.parse(window.localStorage.getItem(STORAGE_KEY) ?? "[]");
    return Array.isArray(value)
      ? value.filter((item): item is string => typeof item === "string")
      : [];
  } catch {
    return [];
  }
}

function writeReservationIds(ids: string[]) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify([...new Set(ids)]));
}

export function getReservationIds(): string[] {
  return readReservationIds();
}

export function rememberReservation(reservationId: string) {
  writeReservationIds([reservationId, ...readReservationIds()]);
}

export function forgetReservations(reservationIds: string[]) {
  const removed = new Set(reservationIds);
  writeReservationIds(readReservationIds().filter((id) => !removed.has(id)));
}
