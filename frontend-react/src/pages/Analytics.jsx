import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import Loader from "../components/Loader";
import EmptyState from "../components/EmptyState";

export default function Analytics() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.analytics().then(setData).catch((e) => setError(e.message));
  }, []);

  if (!data && !error) return <Loader text="Calculating your analytics..." />;

  return (
    <div className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
      <p className="text-xs font-bold uppercase tracking-[.18em] text-cyan-400">Performance</p>
      <h1 className="mt-2 text-3xl font-black">My Analytics</h1>
      <p className="mt-2 text-sm text-slate-600">A view of your completed experiments and scores.</p>

      {error && <div className="mt-5 rounded-xl bg-red-400/10 p-4 text-sm text-red-300">{error}</div>}

      {data && (
        <>
          <div className="mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Metric label="Total attempts" value={data.total_attempts} />
            <Metric label="Completed" value={data.completed_attempts} />
            <Metric label="Average score" value={data.average_score} />
            <Metric label="Best score" value={data.best_score} />
          </div>

          <section className="mt-8 rounded-2xl border border-white/[.07] bg-white/[.02] p-6">
            <h2 className="font-bold">Scores by experiment</h2>
            {!data.per_experiment?.length ? (
              <div className="py-10"><EmptyState title="No completed attempts yet" text="Go finish a lab experiment and your scores will appear here." /></div>
            ) : (
              <div className="mt-6 space-y-4">
                {data.per_experiment.map((x, i) => {
                  const percent = x.max_score ? Math.min(100, (x.score / x.max_score) * 100) : 0;
                  return (
                    <div key={i}>
                      <div className="flex justify-between gap-4 text-sm">
                        <span className="truncate">{x.experiment_title}</span>
                        <span className="font-bold text-cyan-400">{x.score}/{x.max_score}</span>
                      </div>
                      <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/[.06]">
                        <div className="h-full rounded-full bg-cyan-400" style={{ width: `${percent}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {data.per_experiment?.length > 0 && (
            <section className="mt-5 rounded-2xl border border-white/[.07] bg-white/[.02] p-6">
              <h2 className="font-bold">Attempt history</h2>
              <div className="mt-5 overflow-x-auto">
                <table className="w-full min-w-[650px] text-left text-sm">
                  <thead className="border-b border-white/[.06] text-xs uppercase tracking-wider text-slate-600">
                    <tr><th className="px-3 py-3">Experiment</th><th className="px-3 py-3">Score</th><th className="px-3 py-3">Max</th><th className="px-3 py-3">Completed</th></tr>
                  </thead>
                  <tbody>
                    {data.per_experiment.map((x, i) => (
                      <tr key={i} className="border-b border-white/[.04]">
                        <td className="px-3 py-3">{x.experiment_title}</td>
                        <td className="px-3 py-3 font-bold text-cyan-400">{x.score}</td>
                        <td className="px-3 py-3 text-slate-500">{x.max_score}</td>
                        <td className="px-3 py-3 text-slate-500">{x.completed_at ? x.completed_at.slice(0,16).replace("T"," ") : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}

function Metric({ label, value }) {
  return <div className="rounded-2xl border border-white/[.07] bg-white/[.02] p-5"><p className="text-xs text-slate-600">{label}</p><p className="mt-2 text-2xl font-black">{value}</p></div>;
}