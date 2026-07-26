import { createBrowserRouter } from "react-router-dom";

import { HomePage, homeLoader } from "./routes/home";
import {
  ReservationPage,
  reservationAction,
  reservationLoader,
} from "./routes/reservation";
import {
  ReservationCompletePage,
  reservationCompleteLoader,
} from "./routes/reservationComplete";
import { ErrorPage, RootLayout } from "./routes/root";
import { RoomTypePage, roomTypeAction, roomTypeLoader } from "./routes/roomType";

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <HomePage />, loader: homeLoader },
      {
        path: "rooms/:slug",
        element: <RoomTypePage />,
        loader: roomTypeLoader,
        action: roomTypeAction,
      },
      {
        path: "reservations/:slug",
        element: <ReservationPage />,
        loader: reservationLoader,
        action: reservationAction,
      },
      {
        path: "reservations/:slug/complete",
        element: <ReservationCompletePage />,
        loader: reservationCompleteLoader,
      },
    ],
  },
]);
