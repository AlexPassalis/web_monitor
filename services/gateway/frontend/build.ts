import twPlugin from "bun-plugin-tailwind";

console.info("📦 Building frontend...");

const result = await Bun.build({
  entrypoints: ["./src/main.tsx"],
  outdir: "./dist",
  plugins: [twPlugin],
  minify: true,
  sourcemap: "linked",
  target: "browser",
  format: "iife",
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
});

console.info("✅ Build completed. Result:");
console.info("🔍", result);
