export default function Logo({ compact = false }) {
  return (
    <div className="flex items-center gap-2.5">
      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400 font-black text-slate-950 shadow-glow">
        E
      </div>
      {!compact && (
        <div className="text-lg font-black tracking-tight text-white">
          ENGi<span className="text-cyan-400">Twin</span>
        </div>
      )}
    </div>
  );
}