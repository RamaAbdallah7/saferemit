import { useEffect, useState } from "react";
import ScenarioTabs from "./components/ScenarioTabs";
import AppMock from "./components/AppMock";
import ReasoningPanel from "./components/ReasoningPanel";
import { fetchScenarios, fetchHealth, decide, CUSTOM_DEFAULT } from "./api";

const CUSTOM_ID = "__custom__";
const CUSTOM_TAB = {
  id: CUSTOM_ID,
  title: "Custom request",
  description: "Send any request the agent would receive in production — pick the action, edit the signals, and watch it decide.",
  request: CUSTOM_DEFAULT,
};

export default function App() {
  const [scenarios, setScenarios] = useState([]);
  const [health, setHealth] = useState(null);
  const [activeId, setActiveId] = useState(CUSTOM_ID);
  const [form, setForm] = useState(CUSTOM_DEFAULT);
  const [dirty, setDirty] = useState(false);
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [runKey, setRunKey] = useState(0);
  const [error, setError] = useState(null);

  const live = health?.camara_mode === "live";

  useEffect(() => {
    Promise.all([fetchScenarios(), fetchHealth().catch(() => null)])
      .then(([list, h]) => {
        setScenarios(list);
        setHealth(h);
        if (list.length) {
          setActiveId(list[0].id);
          setForm(seedFor(list[0], h?.camara_mode === "live"));
          setDirty(false);
        }
      })
      .catch((e) => setError(e.message));
  }, []);

  function seedFor(scenario, isLive) {
    const req = { ...CUSTOM_DEFAULT, ...(scenario.request || {}) };
    if (isLive && scenario.live_phone) req.phone_number = scenario.live_phone;
    return req;
  }

  function handleSelect(id) {
    const scenario = id === CUSTOM_ID ? CUSTOM_TAB : scenarios.find((s) => s.id === id);
    setActiveId(id);
    setForm(seedFor(scenario || CUSTOM_TAB, live));
    setDirty(false);
    setResult(null);
    setError(null);
  }

  function updateForm(patch) {
    setForm((f) => ({ ...f, ...patch }));
    setDirty(true);
  }

  async function handleRun() {
    setRunning(true);
    setError(null);
    try {
      // An untouched named scenario runs through its scripted path (which
      // keeps the tuned outcome + the live simulator number). Any edit, or
      // the Custom tab, sends the form as a free-form request.
      const asScenario = activeId !== CUSTOM_ID && !dirty;
      const data = await decide(asScenario ? activeId : form);
      setResult(data);
      setRunKey((k) => k + 1);
    } catch (e) {
      setError(e.message);
      setResult(null);
    } finally {
      setRunning(false);
    }
  }

  const tabs = [...scenarios, CUSTOM_TAB];
  const activeScenario =
    activeId === CUSTOM_ID ? CUSTOM_TAB : scenarios.find((s) => s.id === activeId) || CUSTOM_TAB;
  const camaraMode = health?.camara_mode ?? "…";

  return (
    <div className="app">
      <header className="top">
        <div className="brand">
          <span className="brand-mark">SR</span>
          <div>
            <h1>SafeRemit</h1>
            <p>AI-orchestrated anti-fraud layer for cross-border remittances</p>
          </div>
        </div>
        <div className="header-right">
          <span className={`mode-pill ${camaraMode}`} title="Where the network signals come from">
            <span className="dot" />
            {camaraMode === "live" ? "LIVE · Nokia NaC" : camaraMode === "mock" ? "MOCK data" : "…"}
          </span>
          <ScenarioTabs scenarios={tabs} activeId={activeId} onSelect={handleSelect} />
        </div>
      </header>

      <main className="stage">
        <AppMock
          scenario={activeScenario}
          form={form}
          dirty={dirty}
          onChange={updateForm}
          onRun={handleRun}
          running={running}
        />
        <ReasoningPanel result={result} runKey={runKey} />
      </main>

      {error && (
        <p className="run-error">
          Request failed — is the backend running on :8000? ({error})
        </p>
      )}

      <footer className="foot">
        Backend: FastAPI + LangGraph orchestrating CAMARA APIs (SIM Swap, Number Verification, Device
        Status, Location Verification) on Nokia Network-as-Code. Live calls fall back to cached data per{" "}
        <code>PROTOTYPE_NOTES.md</code>.
      </footer>
    </div>
  );
}
