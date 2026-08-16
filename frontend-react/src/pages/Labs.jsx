import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api";
import Loader from "../components/Loader";
import EmptyState from "../components/EmptyState";

const BENCH_TYPES = {
  "": "Manual measurement",
  dso: "DSO + Function Generator",
};

export default function Labs({ user }) {
  const [searchParams] = useSearchParams();
  const selectedCategory = searchParams.get("category");
  const [labs, setLabs] = useState([]);
  const [experiments, setExperiments] = useState({});
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  const canCreate = ["teacher", "institution_admin", "independent_user"].includes(user?.role);

  async function load() {
    setLoading(true);
    try {
      const list = await api.labs();
      setLabs(list);
      const pairs = await Promise.all(
        list.map(async (lab) => [lab.id, await api.experiments(lab.id)])
      );
      setExperiments(Object.fromEntries(pairs));
    } catch (e) {
      setMessage(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  const visibleLabs = useMemo(
    () => selectedCategory ? labs.filter((x) => x.category === selectedCategory) : labs,
    [labs, selectedCategory]
  );

  if (loading) return <Loader text="Loading labs..." />;

  return (
    <div className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-xs font-bold uppercase tracking-[.18em] text-cyan-400">Laboratory</p>
          <h1 className="mt-2 text-3xl font-black">{selectedCategory || "All Labs"}</h1>
          <p className="mt-2 text-sm text-slate-600">Choose an experiment and enter the virtual lab.</p>
        </div>
        {canCreate && (
          <button onClick={() => setShowCreate((v) => !v)} className="rounded-xl bg-cyan-400 px-5 py-3 text-sm font-bold text-slate-950">
            + Create lab
          </button>
        )}
      </div>

      {message && <div className="mt-5 rounded-xl bg-red-400/10 p-4 text-sm text-red-300">{message}</div>}

      {showCreate && <CreateLab onDone={() => {setShowCreate(false); load();}} />}

      {!visibleLabs.length ? (
        <div className="mt-8"><EmptyState title="No labs here yet" text="Create a lab or choose another subject." /></div>
      ) : (
        <div className="mt-8 space-y-4">
          {visibleLabs.map((lab) => (
            <LabCard key={lab.id} lab={lab} experiments={experiments[lab.id] || []} canCreate={canCreate} onReload={load} />
          ))}
        </div>
      )}
    </div>
  );
}

function LabCard({ lab, experiments, canCreate, onReload }) {
  const [show, setShow] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", max_score: 100, bench: "" });
  const [error, setError] = useState("");

  async function createExperiment(e) {
    e.preventDefault();
    setError("");
    try {
      await api.createExperiment(lab.id, form.title, form.description, form.bench ? { bench: form.bench } : {}, Number(form.max_score));
      setForm({ title: "", description: "", max_score: 100, bench: "" });
      setShow(false);
      onReload();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="rounded-2xl border border-white/[.07] bg-white/[.02] p-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-cyan-400">{lab.category}</p>
          <h2 className="mt-2 text-xl font-black">{lab.title}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{lab.description}</p>
        </div>
        {canCreate && <button onClick={() => setShow((v) => !v)} className="h-fit rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-slate-400 hover:text-white">+ Experiment</button>}
      </div>

      {show && (
        <form onSubmit={createExperiment} className="mt-5 grid gap-3 rounded-2xl border border-cyan-400/10 bg-cyan-400/[.02] p-4 md:grid-cols-2">
          <input required placeholder="Experiment title" value={form.title} onChange={(e) => setForm({...form,title:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-4 py-3 text-sm outline-none" />
          <input placeholder="Description" value={form.description} onChange={(e) => setForm({...form,description:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-4 py-3 text-sm outline-none" />
          <input type="number" placeholder="Max score" value={form.max_score} onChange={(e) => setForm({...form,max_score:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-4 py-3 text-sm outline-none" />
          <select value={form.bench} onChange={(e) => setForm({...form,bench:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-4 py-3 text-sm outline-none">
            {Object.entries(BENCH_TYPES).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          {error && <p className="text-xs text-red-300 md:col-span-2">{error}</p>}
          <button className="rounded-xl bg-cyan-400 px-4 py-3 text-sm font-bold text-slate-950 md:col-span-2">Create experiment</button>
        </form>
      )}

      <div className="mt-6 space-y-2">
        {!experiments.length ? <p className="text-sm text-slate-600">No experiments in this lab yet.</p> :
          experiments.map((exp) => {
            const bench = exp.simulation_config?.bench;
            return (
              <div key={exp.id} className="flex flex-col gap-4 rounded-xl border border-white/[.06] bg-white/[.015] p-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-sm font-bold">{exp.title}</h3>
                    <span className={`rounded-md px-2 py-1 text-[9px] font-black ${bench === "dso" ? "bg-green-400/10 text-green-400" : "bg-yellow-400/10 text-yellow-400"}`}>
                      {bench === "dso" ? "LIVE SIMULATOR" : "MANUAL"}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-600">{exp.description} · Max score {exp.max_score}</p>
                </div>
                <Link to={`/simulation/${exp.id}`} className="rounded-lg bg-cyan-400 px-4 py-2.5 text-center text-xs font-bold text-slate-950">Start →</Link>
              </div>
            );
          })}
      </div>
    </div>
  );
}

function CreateLab({ onDone }) {
  const [form, setForm] = useState({title:"",description:"",category:"general"});
  const [error, setError] = useState("");
  async function submit(e) {
    e.preventDefault();
    try { await api.createLab(form.title, form.description, form.category); onDone(); }
    catch (e) { setError(e.message); }
  }
  return (
    <form onSubmit={submit} className="mt-6 grid gap-3 rounded-2xl border border-cyan-400/10 bg-cyan-400/[.02] p-5 md:grid-cols-3">
      <input required placeholder="Lab title" value={form.title} onChange={(e)=>setForm({...form,title:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-4 py-3 text-sm outline-none" />
      <input placeholder="Description" value={form.description} onChange={(e)=>setForm({...form,description:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-4 py-3 text-sm outline-none" />
      <input placeholder="Category / subject" value={form.category} onChange={(e)=>setForm({...form,category:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-4 py-3 text-sm outline-none" />
      {error && <p className="text-xs text-red-300 md:col-span-3">{error}</p>}
      <button className="rounded-xl bg-cyan-400 px-4 py-3 text-sm font-bold text-slate-950 md:col-span-3">Create lab</button>
    </form>
  );
}