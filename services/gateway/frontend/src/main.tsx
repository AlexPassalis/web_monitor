import "@mantine/core/styles.css"
import "@mantine/notifications/styles.css"
import "@mantine/carousel/styles.css"
import "@/index.css"

import { createRoot } from "react-dom/client"
import { BrowserRouter, Routes, Route } from "react-router-dom"

import { ColorSchemeScript, MantineProvider, createTheme } from "@mantine/core"
import { Notifications } from "@mantine/notifications"

const customTheme = createTheme({
  breakpoints: {
    sm: "40em", // 640px
    md: "48em", // 768px
    lg: "64em", // 1024px
    xl: "80em", // 1280px
    "2xl": "96em", // 1536px
  },
  colors: {
    red: [
      "oklch(0.971 0.013 17.380)", // red-050
      "oklch(0.936 0.032 17.717)", // red-100
      "oklch(0.885 0.062 18.334)", // red-200
      "oklch(0.808 0.114 19.571)", // red-300
      "oklch(0.704 0.191 22.216)", // red-400
      "oklch(0.637 0.237 25.331)", // red-500
      "oklch(0.577 0.245 27.325)", // red-600
      "oklch(0.505 0.213 27.518)", // red-700
      "oklch(0.444 0.177 26.899)", // red-800
      "oklch(0.396 0.141 25.723)", // red-900
      "oklch(0.258 0.092 26.042)", // red-950
    ],
    green: [
      "oklch(0.982 0.018 155.826)", // green-050
      "oklch(0.962 0.044 156.743)", // green-100
      "oklch(0.925 0.084 155.995)", // green-200
      "oklch(0.871 0.150 154.449)", // green-300
      "oklch(0.792 0.209 151.711)", // green-400
      "oklch(0.723 0.219 149.579)", // green-500
      "oklch(0.627 0.194 149.214)", // green-600
      "oklch(0.527 0.154 150.069)", // green-700
      "oklch(0.448 0.119 151.328)", // green-800
      "oklch(0.393 0.095 152.535)", // green-900
      "oklch(0.266 0.065 152.934)", // green-950
    ],
    blue: [
      "oklch(0.970 0.014 254.604)", // blue-050
      "oklch(0.932 0.032 255.585)", // blue-100
      "oklch(0.882 0.059 254.128)", // blue-200
      "oklch(0.809 0.105 251.813)", // blue-300
      "oklch(0.707 0.165 254.624)", // blue-400
      "oklch(0.623 0.214 259.815)", // blue-500
      "oklch(0.546 0.245 262.881)", // blue-600
      "oklch(0.488 0.243 264.376)", // blue-700
      "oklch(0.424 0.199 265.638)", // blue-800
      "oklch(0.379 0.146 265.522)", // blue-900
      "oklch(0.282 0.091 267.935)", // blue-950
    ],
  },
})

function start() {
  const root = createRoot(document.getElementById("root")!)
  root.render(
    <>
      <ColorSchemeScript />
      <MantineProvider theme={customTheme}>
        <Notifications />
        <App />
      </MantineProvider>
    </>
  )
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start)
} else {
  start()
}

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
