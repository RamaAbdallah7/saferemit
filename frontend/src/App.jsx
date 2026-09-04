import { useEffect, useRef, useState } from "react";
import ScenarioTabs from "./components/ScenarioTabs";
import AppMock from "./components/AppMock";
import ReasoningPanel from "./components/ReasoningPanel";
import Story from "./components/Story";
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
  const toolRef = useRef(null);

  const live = health?.camara_mode === "live";
  const geminiOn = (health?.assessment_mode || "").includes("gemini");

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
    setResult(null);
    try {
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
      <header className="masthead">
        <span className="wordmark">SafeRemit</span>
        <div className="masthead-status">
          <span className={`chip ${camaraMode === "live" ? "on" : ""}`}>
            <span className="dot" />
            {camaraMode === "live" ? "Live · Nokia NaC" : camaraMode === "mock" ? "Mock data" : "connecting…"}
          </span>
          {geminiOn && (
            <span className="chip on">
              <span className="dot" />
              Gemini analyst
            </span>
          )}
        </div>
      </header>

      <Story onStart={() => toolRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })} />

      <div className="tool" ref={toolRef}>
        <div className="tool-head">
          <h2>The checkpoint</h2>
          <p>
            Every request below hits the same <code>/api/decide</code> endpoint a real
            remittance app would call — the signals and the score are the agent's, not the UI's.
          </p>
          <div className="scenario-picker">
            <span className="scenario-picker-label">Scenario</span>
            <ScenarioTabs scenarios={tabs} activeId={activeId} onSelect={handleSelect} />
          </div>
        </div>

        <main className="stage">
          <AppMock
            scenario={activeScenario}
            form={form}
            dirty={dirty}
            onChange={updateForm}
            onRun={handleRun}
            running={running}
          />
          <ReasoningPanel result={result} runKey={runKey} running={running} />
        </main>

        {error && (
          <p className="run-error">
            Request failed — is the backend running on :8000? ({error})
          </p>
        )}
      </div>

      <footer className="foot">
        <p>
          Backend: FastAPI + LangGraph orchestrating CAMARA APIs — SIM Swap, Number
          Verification, Device Status, Location Verification — on Nokia Network-as-Code.
          Live calls fall back to cached demo data when a network signal is unavailable.
        </p>
        <p className="foot-src">
          Stat sources: World Bank / KNOMAD Migration &amp; Development Brief; UK Finance
          Annual Fraud Report; FBI Internet Crime Complaint Center.
        </p>
      </footer>
    </div>
  );
}
