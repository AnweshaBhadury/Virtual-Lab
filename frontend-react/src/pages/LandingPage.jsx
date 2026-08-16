import { useNavigate } from "react-router-dom";
import Logo from "../components/Logo";

const subjects = [
  ["◉", "Physics", "Physical principles & experiments"],
  ["ϟ", "Electrical", "Circuits & electronics"],
  ["⌁", "Computer Networks", "Networks & protocols"],
  ["▤", "DBMS", "Databases & SQL"],
  ["⚙", "Mechanical", "Mechanical systems"],
  ["01", "Digital", "Digital electronics"],
  ["⚗", "Chemistry", "Chemical experiments"],
  ["+", "More", "Discover more labs"],
];

const features = [
  ["01", "Interactive Virtual Labs", "Turn theory into hands-on experiments through a virtual laboratory built for engineering education."],
  ["02", "Learn by Experimenting", "Experiment, observe results, make mistakes and understand concepts without physical-lab limitations."],
  ["03", "Track Your Progress", "Monitor experiments, assignments and performance from one centralized learning workspace."],
];

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen overflow-hidden bg-[#07111f] text-white">
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute -left-40 -top-40 h-[520px] w-[520px] rounded-full bg-cyan-500/10 blur-[140px]" />
        <div className="absolute -right-40 top-1/4 h-[520px] w-[520px] rounded-full bg-blue-500/10 blur-[150px]" />
      </div>

      <nav className="relative z-10 border-b border-white/[0.06] bg-[#07111f]/80 backdrop-blur-xl">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-8">
          <Logo />
          <div className="hidden gap-8 md:flex">
            <a href="#labs" className="text-sm text-slate-500 hover:text-white">Labs</a>
            <a href="#features" className="text-sm text-slate-500 hover:text-white">Features</a>
            <a href="#institutions" className="text-sm text-slate-500 hover:text-white">Institutions</a>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => navigate("/auth")} className="hidden px-4 py-2 text-sm font-semibold text-slate-400 hover:text-white sm:block">
              Log in
            </button>
            <button onClick={() => navigate("/auth")} className="rounded-xl bg-cyan-400 px-5 py-2.5 text-sm font-bold text-slate-950 hover:bg-cyan-300">
              Get Started
            </button>
          </div>
        </div>
      </nav>

      <section className="relative z-10 mx-auto max-w-7xl px-6 pb-24 pt-20 lg:px-8 lg:pb-32 lg:pt-28">
        <div className="grid items-center gap-16 lg:grid-cols-[1.05fr_.95fr]">
          <div>
            <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/[0.07] px-4 py-2">
              <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-400" />
              <span className="text-xs font-bold uppercase tracking-[.18em] text-cyan-300">
                The Virtual Engineering Lab
              </span>
            </div>

            <h1 className="max-w-4xl text-5xl font-black leading-[.95] tracking-[-.04em] sm:text-6xl lg:text-7xl">
              Engineering
              <br />
              <span className="text-cyan-400">learning,</span>
              <br />
              reimagined.
            </h1>

            <p className="mt-7 max-w-xl text-lg leading-8 text-slate-400">
              Learn engineering by doing. Explore virtual labs, run experiments,
              complete assignments and build intuition beyond the textbook.
            </p>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <button onClick={() => navigate("/auth")} className="rounded-xl bg-cyan-400 px-6 py-3.5 font-bold text-slate-950 hover:bg-cyan-300">
                Explore Labs →
              </button>
              <button onClick={() => navigate("/auth")} className="rounded-xl border border-white/10 bg-white/[0.03] px-6 py-3.5 font-semibold hover:bg-white/[0.07]">
                ▶ Start Learning
              </button>
            </div>

            <div className="mt-12 flex flex-wrap gap-8 border-t border-white/[0.08] pt-7">
              {[
                ["8+", "Engineering subjects"],
                ["∞", "Experiments to explore"],
                ["24/7", "Your virtual lab"],
              ].map(([value, label]) => (
                <div key={label}>
                  <div className="text-2xl font-black">{value}</div>
                  <div className="mt-1 text-xs text-slate-600">{label}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-10 rounded-[40px] bg-cyan-400/10 blur-3xl" />
            <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[#0b1728] p-4 shadow-2xl">
              <div className="flex items-center justify-between border-b border-white/[.07] px-3 pb-4">
                <div className="flex gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
                  <span className="h-2.5 w-2.5 rounded-full bg-yellow-400/70" />
                  <span className="h-2.5 w-2.5 rounded-full bg-green-400/70" />
                </div>
                <span className="text-[10px] text-slate-600">ENGiTwin / Virtual Lab</span>
              </div>

              <div className="grid grid-cols-[58px_1fr] gap-4 p-3">
                <div className="flex flex-col items-center gap-4 rounded-2xl border border-white/[.06] bg-white/[.02] py-4">
                  <Logo compact />
                  {["⌂", "◉", "▤", "◈", "⚙"].map((x, i) => (
                    <div key={i} className={`flex h-8 w-8 items-center justify-center rounded-lg text-sm ${i === 1 ? "bg-cyan-400/10 text-cyan-400" : "text-slate-600"}`}>
                      {x}
                    </div>
                  ))}
                </div>

                <div>
                  <p className="text-[10px] uppercase tracking-widest text-cyan-400">Virtual laboratory</p>
                  <h3 className="mt-1 text-xl font-bold">Explore your labs</h3>

                  <div className="mt-5 grid grid-cols-2 gap-3">
                    {subjects.slice(0, 4).map(([icon, title], i) => (
                      <div key={title} className="rounded-2xl border border-white/[.07] bg-white/[.025] p-4">
                        <div className="mb-5 flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
                          {icon}
                        </div>
                        <p className="text-sm font-bold">{title}</p>
                        <p className="mt-1 text-[10px] text-slate-600">{[12, 8, 10, 6][i]} labs</p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-3 rounded-2xl border border-white/[.07] bg-white/[.025] p-4">
                    <div className="flex justify-between">
                      <span className="text-xs font-semibold">Learning progress</span>
                      <span className="text-xs text-cyan-400">72%</span>
                    </div>
                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/5">
                      <div className="h-full w-[72%] rounded-full bg-cyan-400" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="absolute -bottom-7 -left-6 hidden rounded-2xl border border-white/10 bg-[#101d30] p-4 shadow-xl sm:block">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-400/10 text-green-400">✓</div>
                <div>
                  <p className="text-xs font-bold">Experiment completed</p>
                  <p className="mt-0.5 text-[10px] text-slate-500">Physics · 94% score</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="relative z-10 border-y border-white/[.06] bg-white/[.015]">
        <div className="mx-auto max-w-7xl px-6 py-24 lg:px-8">
          <p className="text-xs font-bold uppercase tracking-[.2em] text-cyan-400">Why ENGiTwin</p>
          <h2 className="mt-4 text-4xl font-black tracking-tight sm:text-5xl">
            Stop just reading.<br /><span className="text-slate-600">Start experimenting.</span>
          </h2>

          <div className="mt-14 grid gap-px overflow-hidden rounded-3xl border border-white/[.07] bg-white/[.07] md:grid-cols-3">
            {features.map(([number, title, description]) => (
              <div key={number} className="bg-[#07111f] p-8 hover:bg-[#0a1728] lg:p-10">
                <span className="text-sm font-bold text-cyan-400">{number}</span>
                <h3 className="mt-12 text-xl font-bold">{title}</h3>
                <p className="mt-4 text-sm leading-7 text-slate-500">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="labs" className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8">
        <p className="text-xs font-bold uppercase tracking-[.2em] text-cyan-400">Explore</p>
        <h2 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">Your engineering world.</h2>
        <p className="mt-4 max-w-xl text-slate-500">
          Choose a subject and enter a dedicated collection of experiments designed for learning through practice.
        </p>

        <div className="mt-12 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {subjects.map(([icon, title, description]) => (
            <button key={title} onClick={() => navigate("/auth")} className="group rounded-2xl border border-white/[.07] bg-white/[.02] p-5 text-left hover:-translate-y-1 hover:border-cyan-400/30 hover:bg-cyan-400/[.04]">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-white/[.03] text-sm font-bold text-cyan-400">
                {icon}
              </div>
              <h3 className="mt-5 text-sm font-bold">{title}</h3>
              <p className="mt-1 text-xs leading-5 text-slate-600">{description}</p>
            </button>
          ))}
        </div>
      </section>

      <section id="institutions" className="relative z-10 mx-auto max-w-7xl px-6 pb-24 lg:px-8">
        <div className="overflow-hidden rounded-[32px] border border-white/10 bg-gradient-to-br from-[#0d2033] to-[#091522]">
          <div className="grid lg:grid-cols-2">
            <div className="p-8 sm:p-12 lg:p-16">
              <p className="text-xs font-bold uppercase tracking-[.2em] text-cyan-400">For institutions</p>
              <h2 className="mt-5 text-4xl font-black tracking-tight sm:text-5xl">
                One platform.<br /><span className="text-slate-600">The whole institution.</span>
              </h2>
              <p className="mt-6 max-w-lg leading-7 text-slate-400">
                Give students and teachers a shared virtual laboratory environment while keeping learning, assignments and progress organized in one place.
              </p>
              <div className="mt-8 space-y-4">
                {["Student & teacher accounts", "Institution-based access", "Shareable institution codes", "Assignments & analytics"].map((x) => (
                  <div key={x} className="flex items-center gap-3 text-sm text-slate-300">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-cyan-400/10 text-cyan-400">✓</span>{x}
                  </div>
                ))}
              </div>
              <button onClick={() => navigate("/auth")} className="mt-9 rounded-xl bg-white px-5 py-3 text-sm font-bold text-slate-950 hover:bg-slate-200">
                Build your lab →
              </button>
            </div>

            <div className="hidden min-h-[450px] items-center justify-center lg:flex">
              <div className="w-[330px] rounded-3xl border border-cyan-400/20 bg-[#081521]/90 p-5 shadow-2xl">
                <div className="flex justify-between">
                  <span className="text-xs font-bold">Institution Dashboard</span>
                  <span className="rounded-full bg-green-400/10 px-2 py-1 text-[9px] text-green-400">ACTIVE</span>
                </div>
                <div className="mt-5 grid grid-cols-3 gap-2">
                  {[["248","Students"],["32","Teachers"],["86","Labs"]].map(([n,l]) => (
                    <div key={l} className="rounded-xl bg-white/[.04] p-3">
                      <p className="text-lg font-black">{n}</p><p className="mt-1 text-[9px] text-slate-600">{l}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-3 rounded-xl bg-white/[.04] p-4">
                  <p className="text-[10px] font-semibold text-slate-400">Student activity</p>
                  <div className="mt-4 flex h-24 items-end gap-2">
                    {[35,55,42,70,58,82,68,92,76,88].map((h,i) => <div key={i} className="flex-1 rounded-t bg-cyan-400/60" style={{height:`${h}%`}} />)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="relative z-10 border-t border-white/[.06]">
        <div className="mx-auto max-w-4xl px-6 py-28 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-400 text-2xl text-slate-950">🧪</div>
          <h2 className="mt-7 text-4xl font-black tracking-tight sm:text-6xl">Your lab is waiting.</h2>
          <p className="mx-auto mt-5 max-w-xl text-slate-500">Step beyond the textbook. Experiment, learn and build your engineering intuition with ENGiTwin.</p>
          <button onClick={() => navigate("/auth")} className="mt-8 rounded-xl bg-cyan-400 px-7 py-4 font-bold text-slate-950 hover:bg-cyan-300">Get Started →</button>
        </div>
      </section>

      <footer className="border-t border-white/[.06]">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-6 py-8 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <Logo />
          <p className="text-xs text-slate-600">© 2026 ENGiTwin. Learn by doing.</p>
        </div>
      </footer>
    </div>
  );
}