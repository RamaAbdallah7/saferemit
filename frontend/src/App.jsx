import { useEffect, useState } from "react";
import ScenarioTabs from "./components/ScenarioTabs";
import AppMock from "./components/AppMock";
import ReasoningPanel from "./components/ReasoningPanel";
import { fetchScenarios, decide } from "./api";

export default function App() {
  const [scenarios, setScenarios] = useState([]);
  const [activeId, setActiveId] = useState(null);
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
      const data = await decide(activeId);
      setResult(data);
      setRunKey((k) => k + 1);
    } catch (e) {
      setError(e.message);
      setResult(null);
    } finally {
      setRunning(false);
    }
  }

  const activeScenario = scenarios.find((s) => s.id === activeId) || null;

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
        <ScenarioTabs scenarios={scenarios} activeId={activeId} onSelect={handleSelect} />
      </header>

      <main className="stage">
        <AppMock scenario={activeScenario} onRun={handleRun} running={running} />
        <ReasoningPanel result={result} runKey={runKey} />
      </main>

      {error && (
        <p style={{ textAlign: "center", color: "var(--danger)", padding: "0 28px" }}>
          Request failed — is the backend running on :8000? ({error})
        </p>
      )}

      <footer className="foot">
        Backend: FastAPI + LangGraph orchestrating mock CAMARA APIs (SIM Swap, Number Verification, Device
        Status, Location Verification) on the Nokia Network-as-Code shape. Swap the mocks for live calls per{" "}
        <code>PROTOTYPE_NOTES.md</code>.
      </footer>
    </div>
  );
}
