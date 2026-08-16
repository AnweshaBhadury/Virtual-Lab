import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import Loader from "../components/Loader";
import DSO_HTML from "../assets/dso.html?raw";

export default function Simulation() {
  const { experimentId } = useParams();
  const navigate = useNavigate();
  const [experiment, setExperiment] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [measurements, setMeasurements] = useState([
    { key: "", value: "" },
    { key: "", value: "" },
  ]);
  const [history, setHistory] = useState([]);
  const [chat, setChat] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const iframeRef = useRef(null);

  useEffect(() => {
    let mounted = true;
    async function init() {
      try {
        const exp = await api.experiment(experimentId);
        const started = await api.startAttempt(exp.id);
        const h = await api.aiHistory(started.id).catch(() => []);
        if (mounted) {
          setExperiment(exp);
          setAttempt(started);
          setHistory(h);
        }
      } catch (e) {
        if (mounted) setError(e.message);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    init();
    return () => { mounted = false; };
  }, [experimentId]);

  const isDSO = useMemo(
    () => experiment?.simulation_config?.bench === "dso",
    [experiment]
  );

  async function startAI() {
    if (!attempt) return;
    setBusy(true);
    try {
      const reply = await api.aiAsk(attempt.id);
      setHistory([reply]);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function sendAI() {
    if (!chat.trim() || !attempt) return;
    const message = chat.trim();
    setChat("");
    setHistory((old) => [...old, { role: "student", content: message, created_at: "" }]);
    setBusy(true);
    try {
      const reply = await api.aiAsk(attempt.id, message);
      setHistory((old) => [...old, reply]);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function complete() {
    const clean = {};
    for (const row of measurements) {
      if (row.key.trim()) clean[row.key.trim()] = row.value;
    }
    if (!Object.keys(clean).length) {
      setError("Add at least one measurement before completing the attempt.");
      return;
    }

    setBusy(true);
    setError("");
    try {
      const data = await api.completeAttempt(attempt.id, clean);
      setResult(data.result);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Loader text="Opening your experiment..." />;

  if (error && !experiment) {
    return <div className="mx-auto max-w-3xl p-8"><div className="rounded-2xl bg-red-400/10 p-5 text-red-300">{error}</div></div>;
  }

  if (!experiment || !attempt) return null;

  return (
    <div className="mx-auto max-w-[1600px] px-4 py-5 lg:px-6">
      <div className="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <Link to="/labs" className="text-xs font-bold text-cyan-400">← Labs</Link>
          <h1 className="mt-2 text-2xl font-black">{experiment.title}</h1>
          <p className="mt-1 text-sm text-slate-600">{experiment.description}</p>
        </div>
        <span className="rounded-full border border-white/10 px-3 py-2 text-xs text-slate-500">
          Attempt #{attempt.id}
        </span>
      </div>

      {error && <div className="mb-4 rounded-xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-300">{error}</div>}

      {result && (
        <div className="mb-5 rounded-2xl border border-cyan-400/20 bg-cyan-400/[.06] p-6">
          <p className="text-xs font-bold uppercase tracking-widest text-cyan-400">Attempt complete</p>
          <p className="mt-2 text-3xl font-black">{result.score} / {result.max_score}</p>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">{result.ai_feedback}</p>
          <button onClick={() => navigate("/analytics")} className="mt-5 rounded-xl bg-cyan-400 px-4 py-3 text-sm font-bold text-slate-950">View analytics →</button>
        </div>
      )}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <section className="min-w-0 rounded-2xl border border-white/[.07] bg-[#0a1626] p-3">
          {isDSO ? (
            <iframe
              ref={iframeRef}
              title="ENGiTwin DSO simulator"
              srcDoc={DSO_HTML}
              className="h-[1500px] w-full rounded-xl border-0 bg-transparent"
              sandbox="allow-scripts allow-same-origin"
            />
          ) : (
            <div className="flex min-h-[500px] items-center justify-center rounded-xl border border-dashed border-white/10 p-10 text-center">
              <div>
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-yellow-400/10 text-yellow-400">◌</div>
                <h2 className="mt-5 font-bold">Manual experiment</h2>
                <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
                  This experiment does not have an interactive simulator yet. Enter your readings in the result panel.
                </p>
              </div>
            </div>
          )}
        </section>

        <aside className="space-y-5">
          <section className="rounded-2xl border border-white/[.07] bg-[#0a1626] p-5">
            <h2 className="font-bold">Submit your results</h2>
            <p className="mt-1 text-xs leading-5 text-slate-600">Enter the measurements produced by your experiment.</p>

            <div className="mt-5 space-y-2">
              {measurements.map((row, i) => (
                <div key={i} className="grid grid-cols-[1fr_1fr_auto] gap-2">
                  <input placeholder="Name" value={row.key} onChange={(e) => setMeasurements((m) => m.map((x,j)=>j===i?{...x,key:e.target.value}:x))} className="min-w-0 rounded-lg border border-white/10 bg-[#07111f] px-3 py-2 text-xs outline-none" />
                  <input placeholder="Value" value={row.value} onChange={(e) => setMeasurements((m) => m.map((x,j)=>j===i?{...x,value:e.target.value}:x))} className="min-w-0 rounded-lg border border-white/10 bg-[#07111f] px-3 py-2 text-xs outline-none" />
                  <button onClick={() => setMeasurements((m)=>m.filter((_,j)=>j!==i))} className="rounded-lg px-2 text-slate-600 hover:text-red-300">×</button>
                </div>
              ))}
            </div>

            <button onClick={() => setMeasurements((m)=>[...m,{key:"",value:""}])} className="mt-3 text-xs font-bold text-cyan-400">+ Add measurement</button>
            <button disabled={busy || !!result} onClick={complete} className="mt-5 w-full rounded-xl bg-cyan-400 py-3 text-sm font-bold text-slate-950 disabled:opacity-40">
              {busy ? "Submitting..." : result ? "Completed" : "Complete Attempt"}
            </button>
          </section>

          <section className="rounded-2xl border border-white/[.07] bg-[#0a1626] p-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-bold">AI Lab Assistant</h2>
                <p className="mt-1 text-[11px] text-slate-600">One question at a time. Think it through.</p>
              </div>
              <span className="text-lg">🤖</span>
            </div>

            <div className="mt-4 max-h-[420px] min-h-[180px] space-y-3 overflow-y-auto rounded-xl bg-[#07111f] p-3">
              {!history.length ? (
                <div className="flex h-40 items-center justify-center text-center">
                  <div>
                    <p className="text-sm text-slate-500">Ready when you are.</p>
                    <button onClick={startAI} disabled={busy} className="mt-3 rounded-lg bg-white/[.05] px-3 py-2 text-xs font-bold text-cyan-300 disabled:opacity-40">
                      Start conversation
                    </button>
                  </div>
                </div>
              ) : history.map((msg, i) => (
                <div key={i} className={msg.role === "assistant" ? "mr-6" : "ml-6"}>
                  <div className={`rounded-xl p-3 text-xs leading-5 ${msg.role === "assistant" ? "bg-white/[.05] text-slate-300" : "bg-cyan-400/10 text-cyan-200"}`}>
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-3 flex gap-2">
              <input
                value={chat}
                onChange={(e) => setChat(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") sendAI(); }}
                placeholder="Answer the assistant..."
                className="min-w-0 flex-1 rounded-xl border border-white/10 bg-[#07111f] px-3 py-3 text-xs outline-none focus:border-cyan-400/40"
              />
              <button onClick={sendAI} disabled={busy || !chat.trim()} className="rounded-xl bg-cyan-400 px-4 text-xs font-bold text-slate-950 disabled:opacity-40">Send</button>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}