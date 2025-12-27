import "@/index.css"

import { createRoot } from "react-dom/client"
import { BrowserRouter, Routes, Route } from "react-router-dom"

import Auth from "@/app/Auth"
import Home from "@/app/Home"
import Fallback from "@/app/Fallback"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth" element={<Auth />} />
        <Route path="/" element={<Home />} />
        <Route path="*" element={<Fallback />} />
      </Routes>
    </BrowserRouter>
  )
}

function start() {
  const root = createRoot(document.getElementById("root")!)
  root.render(<App />)
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start)
} else {
  start()
}
