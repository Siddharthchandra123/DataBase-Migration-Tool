import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
// @ts-expect-error CSS is handled by the bundler and has no TypeScript declarations.
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);