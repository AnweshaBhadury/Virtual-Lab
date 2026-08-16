export default function EmptyState({ icon = "◌", title, text, action }) {
  return (
    <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.015] p-12 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-400/10 text-xl text-cyan-400">
        {icon}
      </div>
      <h3 className="mt-5 font-bold text-white">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
        {text}
      </p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}