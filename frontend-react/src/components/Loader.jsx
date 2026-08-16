export default function Loader({ text = "Loading..." }) {
  return (
    <div className="flex min-h-[240px] items-center justify-center">
      <div className="text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-white/10 border-t-cyan-400" />
        <p className="mt-4 text-sm text-slate-500">{text}</p>
      </div>
    </div>
  );
}