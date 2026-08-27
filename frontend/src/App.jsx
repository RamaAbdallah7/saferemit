import { useEffect, useState } from "react";
import ScenarioTabs from "./components/ScenarioTabs";
import AppMock from "./components/AppMock";
import ReasoningPanel from "./components/ReasoningPanel";
import { fetchScenarios, fetchHealth, decide, CUSTOM_DEFAULT } from "./api";

const CUSTOM_ID = "__custom__";

export default function App() {
  const [scenarios, setScenarios] = useState([]);
  const [health, setHealth] = useState(null);
  const [activeId, setActiveId] = useState(null);
  const [customReq, setCustomReq] = useState(CUSTOM_DEFAULT);
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [runKey, setRunKey] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchScenarios()
      .then((list) => {
        setScenarios(list);
        if (list.length) setActiveId(list[0].id);
      })
      .catch((e) => setError(e.message));
    fetchHealth().then(setHealth).catch(() => setHealth(null));
  }, []);

  function handleSelect(id) {
    setActiveId(id);
    setResult(null);
    setError(null);
  }

  async function handleRun() {
    if (!activeId) return;
    setRunning(true);
    setError(null);
    try {
      const data = await decide(activeId === CUSTOM_ID ? customReq : activeId);
      setResult(data);
      setRunKey((k) => k + 1);
    } catch (e) {
      setError(e.message);
      setResult(null);
    } finally {
      setRunning(false);
    }
  }

  const tabs = [
    ...scenarios,
    { id: CUSTOM_ID, title: "Custom request" },
  ];
  const isCustom = activeId === CUSTOM_ID;
  const activeScenario = isCustom
    ? { id: CUSTOM_ID, description: "Send any request the agent would receive in production — pick the action, edit the signals, and watch it decide." }
    : scenarios.find((s) => s.id === activeId) || null;

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
          <span className={`mode-pill ${camaraMode}`} title="CAMARA data source (GET /api/health)">
            <span className="dot" />
            {camaraMode === "live" ? "LIVE · Nokia NaC" : camaraMode === "mock" ? "MOCK data" : "…"}
          </span>
          <ScenarioTabs scenarios={tabs} activeId={activeId} onSelect={handleSelect} />
        </div>
      </header>

      <main className="stage">
        <AppMock
          scenario={activeScenario}
          isCustom={isCustom}
          customReq={customReq}
          onCustomChange={setCustomReq}
          onRun={handleRun}
          running={running}
        />
        <ReasoningPanel result={result} runKey={runKey} />
      </main>

      {error && (
        <p style={{ textAlign: "center", color: "var(--danger)", padding: "0 28px" }}>
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
