import "./index.css";

import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import HomePage from "@/app/HomePage";
import CatchAllPage from "@/app/CatchAllPage";

function Frontend() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="*" element={<CatchAllPage />} />
      </Routes>
    </BrowserRouter>
  );
}

function start() {
  const root = createRoot(document.getElementById("root")!);
  root.render(<Frontend />);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start);
} else {
  start();
}
