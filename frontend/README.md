# SafeRemit demo UI

React + Vite + Framer Motion. See the main `README.md` and `PROTOTYPE_NOTES.md` (both one level up) for the full picture — this file is just the frontend-specific commands.

```bash
npm install
npm run dev      # dev server on :5173, proxies /api to the backend on :8000
npm run build    # production build to dist/ — this is what backend/app.py serves
```

Component map: `src/App.jsx` wires everything together. `src/components/` has one file per piece of UI — `ScenarioTabs`, `AppMock` (the mock remittance form), `ReasoningPanel` (wraps `DecisionBadge` + `TraceList`). `src/api.js` is the only file that talks to the backend.

For where to tune the animation specifically, see the "Where to tune the Framer Motion animation" section in `../PROTOTYPE_NOTES.md`.
