import { createBrowserRouter } from "react-router-dom";

import { HomePage } from "./routes/home";
import {
  ReservationPage,
  reservationAction,
  reservationLoader,
} from "./routes/reservation";
import { ErrorPage, RootLayout } from "./routes/root";

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <HomePage /> },
      {
        path: "reservations/:slug",
        element: <ReservationPage />,
        loader: reservationLoader,
        action: reservationAction,
      },
    ],
  },
]);
