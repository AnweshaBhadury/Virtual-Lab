import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, APIError } from "../api";
import Loader from "../components/Loader";
import EmptyState from "../components/EmptyState";

const icons = {
  Physics: "◉",
  Electrical: "ϟ",
  "Computer Networks": "⌁",
  DBMS: "▤",
  Mechanical: "⚙",
  Digital: "01",
  Chemistry: "⚗",
  general: "⌘",
};

export default function Dashboard({ user }) {
  const [labs, setLabs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.labs(), api.analytics(), api.assignments()])
      .then(([l, a, ass]) => {
        setLabs(l);
        setAnalytics(a);
        setAssignments(ass);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader text="Preparing your workspace..." />;

  const categories = [...new Set(labs.map((l) => l.category))];

  return (
    <div className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
      {error && <div className="mb-5 rounded-xl bg-red-400/10 p-4 text-sm text-red-300">{error}</div>}

      <div className="rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-[#10263b] to-[#0a1626] p-7 sm:p-10">
        <p className="text-xs font-bold uppercase tracking-[.18em] text-cyan-400">Learning workspace</p>
        <h1 className="mt-3 text-3xl font-black sm:text-4xl">Welcome back, {user?.name} 👋</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
          Pick a subject, open an experiment and learn by doing.
        </p>
        <Link to="/labs" className="mt-6 inline-block rounded-xl bg-cyan-400 px-5 py-3 text-sm font-bold text-slate-950">Explore labs →</Link>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric title="Attempts" value={analytics?.total_attempts ?? 0} />
        <Metric title="Completed" value={analytics?.completed_attempts ?? 0} />
        <Metric title="Average score" value={analytics?.average_score ?? 0} />
        <Metric title="Best score" value={analytics?.best_score ?? 0} />
      </div>

      <section className="mt-10">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.18em] text-cyan-400">Subjects</p>
            <h2 className="mt-2 text-2xl font-black">Explore your labs</h2>
          </div>
          <Link to="/labs" className="text-xs font-bold text-cyan-400">View all →</Link>
        </div>

        {categories.length === 0 ? (
          <div className="mt-6"><EmptyState title="No labs yet" text="Labs will appear here when your institution or teacher creates them." /></div>
        ) : (
          <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-4">
            {categories.map((cat) => (
              <Link key={cat} to={`/labs?category=${encodeURIComponent(cat)}`} className="rounded-2xl border border-white/[.07] bg-white/[.02] p-5 hover:-translate-y-1 hover:border-cyan-400/30">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">{icons[cat] || "⌘"}</div>
                <h3 className="mt-5 text-sm font-bold">{cat}</h3>
                <p className="mt-1 text-xs text-slate-600">{labs.filter((l) => l.category === cat).length} labs</p>
              </Link>
            ))}
          </div>
        )}
      </section>

      <section className="mt-10 grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/[.07] bg-white/[.02] p-6">
          <div className="flex justify-between">
            <h2 className="font-bold">Recent progress</h2>
            <Link to="/analytics" className="text-xs text-cyan-400">Analytics →</Link>
          </div>
          {analytics?.per_experiment?.length ? (
            <div className="mt-5 space-y-3">
              {analytics.per_experiment.slice(-5).reverse().map((x, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl bg-white/[.025] p-3">
                  <span className="truncate text-sm">{x.experiment_title}</span>
                  <span className="font-bold text-cyan-400">{x.score}/{x.max_score}</span>
                </div>
              ))}
            </div>
          ) : <p className="mt-5 text-sm text-slate-600">Finish an experiment to see your progress here.</p>}
        </div>

        <div className="rounded-2xl border border-white/[.07] bg-white/[.02] p-6">
          <div className="flex justify-between">
            <h2 className="font-bold">Assignments</h2>
            <Link to="/assignments" className="text-xs text-cyan-400">Open →</Link>
          </div>
          {assignments.length ? (
            <div className="mt-5 space-y-3">
              {assignments.slice(0, 4).map((a) => (
                <div key={a.id} className="rounded-xl bg-white/[.025] p-3">
                  <p className="text-sm font-semibold">Experiment #{a.experiment_id}</p>
                  <p className="mt-1 text-xs text-slate-600">{a.due_date ? `Due ${a.due_date.slice(0,10)}` : "No due date"}</p>
                </div>
              ))}
            </div>
          ) : <p className="mt-5 text-sm text-slate-600">Nothing assigned to you yet.</p>}
        </div>
      </section>
    </div>
  );
}

function Metric({ title, value }) {
  return (
    <div className="rounded-2xl border border-white/[.07] bg-white/[.02] p-5">
      <p className="text-xs text-slate-600">{title}</p>
      <p className="mt-2 text-2xl font-black">{value}</p>
    </div>
  );
}