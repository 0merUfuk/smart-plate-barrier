import js from "@eslint/js";
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import tseslint from "typescript-eslint";

export default defineConfig([
  js.configs.recommended,
  ...nextVitals,
  ...tseslint.configs.recommended,
  globalIgnores([".next/**", "out/**", "coverage/**", "next-env.d.ts", "app.js"]),
]);
