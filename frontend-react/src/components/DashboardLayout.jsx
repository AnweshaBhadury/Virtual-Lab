import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import Logo from "./Logo";

const nav = [
  ["dashboard", "⌂", "Dashboard"],
  ["labs", "◉", "Labs"],
  ["assignments", "▤", "Assignments"],
  ["analytics", "◈", "Analytics"],
];

export default function DashboardLayout({ user, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="min-h-screen bg-[#07111f] text-white">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-white/[0.06] bg-[#081321] lg:block">
        <div className="flex h-full flex-col p-5">
          <button onClick={() => navigate("/dashboard")} className="mb-10 text-left">
            <Logo />
          </button>

          <p className="px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-600">
            Workspace
          </p>

          <nav className="mt-3 space-y-1">
            {nav.map(([path, icon, label]) => (
              <NavLink
                key={path}
                to={`/${path}`}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold transition ${
                    isActive
                      ? "bg-cyan-400/10 text-cyan-300"
                      : "text-slate-500 hover:bg-white/[0.03] hover:text-white"
                  }`
                }
              >
                <span className="w-5 text-center">{icon}</span>
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-auto rounded-2xl border border-white/[0.06] bg-white/[0.02] p-3">
            <p className="truncate text-sm font-bold">{user?.name}</p>
            <p className="mt-1 truncate text-xs text-slate-600">{user?.email}</p>
            <p className="mt-3 text-[10px] font-bold uppercase tracking-wider text-cyan-400">
              {user?.role?.replaceAll("_", " ")}
            </p>
            <button
              onClick={onLogout}
              className="mt-4 w-full rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-slate-400 hover:bg-white/[0.04] hover:text-white"
            >
              Log out
            </button>
          </div>
        </div>
      </aside>

      <header className="sticky top-0 z-20 border-b border-white/[0.06] bg-[#07111f]/90 backdrop-blur-xl lg:ml-64">
        <div className="flex h-16 items-center justify-between px-5 lg:px-8">
          <div>
            <p className="text-xs text-slate-600">ENGiTwin</p>
            <p className="text-sm font-semibold">
              {location.pathname === "/dashboard"
                ? "Learning workspace"
                : location.pathname.replace("/", "").replaceAll("-", " ")}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/labs")}
              className="hidden rounded-xl border border-white/10 px-4 py-2 text-xs font-bold text-slate-300 hover:bg-white/[0.04] sm:block"
            >
              Explore labs
            </button>
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-cyan-400 text-xs font-black text-slate-950">
              {user?.name?.charAt(0)?.toUpperCase() || "U"}
            </div>
          </div>
        </div>
      </header>

      <main className="lg:ml-64">
        <div className="border-b border-white/[0.05] bg-[#07111f] lg:hidden">
          <div className="flex gap-1 overflow-x-auto px-4 py-2">
            {nav.map(([path, icon, label]) => (
              <NavLink
                key={path}
                to={`/${path}`}
                className={({ isActive }) =>
                  `whitespace-nowrap rounded-lg px-3 py-2 text-xs font-semibold ${
                    isActive ? "bg-cyan-400/10 text-cyan-300" : "text-slate-500"
                  }`
                }
              >
                {icon} {label}
              </NavLink>
            ))}
          </div>
        </div>

        <Outlet />
      </main>
    </div>
  );
}