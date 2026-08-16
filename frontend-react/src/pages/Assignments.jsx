import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Loader from "../components/Loader";
import EmptyState from "../components/EmptyState";

export default function Assignments({ user }) {
  const [assignments, setAssignments] = useState([]);
  const [labs, setLabs] = useState([]);
  const [students, setStudents] = useState([]);
  const [experimentMap, setExperimentMap] = useState({});
  const [form, setForm] = useState({ lab: "", experiment: "", student: "", due: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const canAssign = user?.role === "teacher";

  async function load() {
    setLoading(true);
    try {
      const ass = await api.assignments();
      setAssignments(ass);
      const l = await api.labs();
      setLabs(l);
      const pairs = await Promise.all(l.map(async (lab) => [lab.id, await api.experiments(lab.id)]));
      setExperimentMap(Object.fromEntries(pairs));
      if (canAssign) {
        const users = await api.users();
        setStudents(users.filter((x) => x.role === "student"));
      }
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, [canAssign]);

  async function assign(e) {
    e.preventDefault();
    setError("");
    try {
      await api.createAssignment(Number(form.experiment), Number(form.student), form.due ? `${form.due}T00:00:00` : null);
      setForm({ lab: "", experiment: "", student: "", due: "" });
      await load();
    } catch (e) { setError(e.message); }
  }

  if (loading) return <Loader text="Loading assignments..." />;

  const experiments = form.lab ? (experimentMap[Number(form.lab)] || []) : [];

  return (
    <div className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
      <p className="text-xs font-bold uppercase tracking-[.18em] text-cyan-400">Learning workflow</p>
      <h1 className="mt-2 text-3xl font-black">Assignments</h1>
      <p className="mt-2 text-sm text-slate-600">Work assigned to you, or assign experiments to your students.</p>

      {error && <div className="mt-5 rounded-xl bg-red-400/10 p-4 text-sm text-red-300">{error}</div>}

      {canAssign && (
        <form onSubmit={assign} className="mt-7 rounded-2xl border border-white/[.07] bg-white/[.02] p-6">
          <h2 className="font-bold">Assign an experiment</h2>
          <div className="mt-5 grid gap-3 md:grid-cols-4">
            <select required value={form.lab} onChange={(e)=>setForm({...form,lab:e.target.value,experiment:""})} className="rounded-xl border border-white/10 bg-[#07111f] px-3 py-3 text-sm">
              <option value="">Choose lab</option>
              {labs.map((l)=><option key={l.id} value={l.id}>{l.title}</option>)}
            </select>
            <select required value={form.experiment} onChange={(e)=>setForm({...form,experiment:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-3 py-3 text-sm">
              <option value="">Choose experiment</option>
              {experiments.map((x)=><option key={x.id} value={x.id}>{x.title}</option>)}
            </select>
            <select required value={form.student} onChange={(e)=>setForm({...form,student:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-3 py-3 text-sm">
              <option value="">Choose student</option>
              {students.map((s)=><option key={s.id} value={s.id}>{s.name} ({s.email})</option>)}
            </select>
            <input type="date" value={form.due} onChange={(e)=>setForm({...form,due:e.target.value})} className="rounded-xl border border-white/10 bg-[#07111f] px-3 py-3 text-sm" />
          </div>
          <button className="mt-4 rounded-xl bg-cyan-400 px-5 py-3 text-sm font-bold text-slate-950">Assign</button>
        </form>
      )}

      <section className="mt-8">
        {!assignments.length ? (
          <EmptyState icon="▤" title="Nothing assigned to you" text="When a teacher assigns an experiment to you, it will appear here." />
        ) : (
          <div className="space-y-3">
            {assignments.map((a) => (
              <AssignmentCard key={a.id} assignment={a} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function AssignmentCard({ assignment }) {
  const [exp, setExp] = useState(null);
  useEffect(() => { api.experiment(assignment.experiment_id).then(setExp).catch(()=>{}); }, [assignment.experiment_id]);

  return (
    <div className="flex flex-col justify-between gap-4 rounded-2xl border border-white/[.07] bg-white/[.02] p-5 sm:flex-row sm:items-center">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-cyan-400">Assignment #{assignment.id}</p>
        <h3 className="mt-2 font-bold">{exp?.title || `Experiment #${assignment.experiment_id}`}</h3>
        <p className="mt-1 text-xs text-slate-600">
          {assignment.due_date ? `Due ${assignment.due_date.slice(0,10)}` : "No due date"} · Teacher #{assignment.teacher_id}
        </p>
      </div>
      {exp && <Link to={`/simulation/${exp.id}`} className="rounded-xl bg-cyan-400 px-4 py-3 text-center text-xs font-bold text-slate-950">Start →</Link>}
    </div>
  );
}