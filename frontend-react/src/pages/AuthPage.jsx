import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Logo from "../components/Logo";
import { api, APIError } from "../api";

export default function AuthPage({ onAuthenticated }) {
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [accountType, setAccountType] = useState("independent");
  const [institutionMode, setInstitutionMode] = useState("join");
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [createdInstitution, setCreatedInstitution] = useState(null);

  const set = (key, value) => setForm((old) => ({ ...old, [key]: value }));

  async function submitLogin(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await api.login(form.email, form.password);
      onAuthenticated(data);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitSignup(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      let institutionCode = null;

      if (accountType === "institution" && institutionMode === "create") {
        const inst = await api.createInstitution(form.institutionName, Number(form.maxStudents || 0));
        institutionCode = inst.code;
        setCreatedInstitution(inst);
      } else if (accountType === "institution") {
        institutionCode = (form.institutionCode || "").trim().toUpperCase();
        if (!institutionCode) throw new APIError("Enter your institution code.");
      }

      const role =
        accountType === "independent"
          ? "independent_user"
          : institutionMode === "create"
          ? "institution_admin"
          : form.role || "student";

      const data = await api.signup(
        form.name,
        form.email,
        form.password,
        role,
        institutionCode
      );

      onAuthenticated(data);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#07111f]">
      <div className="mx-auto flex min-h-screen max-w-7xl items-center px-6 py-10">
        <div className="grid w-full gap-12 lg:grid-cols-2 lg:items-center">
          <div className="hidden lg:block">
            <button onClick={() => navigate("/")}><Logo /></button>
            <p className="mt-16 text-xs font-bold uppercase tracking-[.2em] text-cyan-400">Welcome to ENGiTwin</p>
            <h1 className="mt-5 text-6xl font-black leading-[.95] tracking-tight">
              Build your
              <br /><span className="text-cyan-400">engineering</span>
              <br />intuition.
            </h1>
            <p className="mt-7 max-w-lg leading-7 text-slate-500">
              Sign in to access virtual labs, experiments, assignments, analytics and your institution workspace.
            </p>
          </div>

          <div className="mx-auto w-full max-w-md">
            <div className="mb-8 flex items-center justify-between lg:hidden">
              <button onClick={() => navigate("/")}><Logo /></button>
            </div>

            <div className="rounded-3xl border border-white/[.08] bg-[#0a1626] p-6 shadow-2xl sm:p-8">
              <div className="flex rounded-xl bg-white/[.03] p-1">
                {["login", "signup"].map((x) => (
                  <button key={x} onClick={() => {setMode(x); setError("");}} className={`flex-1 rounded-lg py-2.5 text-sm font-bold ${mode === x ? "bg-white text-slate-950" : "text-slate-500"}`}>
                    {x === "login" ? "Log in" : "Sign up"}
                  </button>
                ))}
              </div>

              <h2 className="mt-8 text-2xl font-black">{mode === "login" ? "Welcome back" : "Create your account"}</h2>
              <p className="mt-2 text-sm text-slate-600">
                {mode === "login" ? "Continue where you left off." : "Choose how you want to use ENGiTwin."}
              </p>

              {error && <div className="mt-5 rounded-xl border border-red-400/20 bg-red-400/10 p-3 text-sm text-red-300">{error}</div>}

              {createdInstitution && (
                <div className="mt-5 rounded-xl border border-cyan-400/20 bg-cyan-400/10 p-4 text-sm">
                  Institution created. Code: <strong className="text-cyan-300">{createdInstitution.code}</strong>
                </div>
              )}

              {mode === "login" ? (
                <form onSubmit={submitLogin} className="mt-7 space-y-4">
                  <Field label="Email" type="email" value={form.email || ""} onChange={(v) => set("email", v)} required />
                  <Field label="Password" type="password" value={form.password || ""} onChange={(v) => set("password", v)} required />
                  <SubmitButton loading={loading}>Log in →</SubmitButton>
                </form>
              ) : (
                <form onSubmit={submitSignup} className="mt-7 space-y-4">
                  <div className="grid grid-cols-2 gap-2">
                    <Choice active={accountType === "independent"} onClick={() => setAccountType("independent")}>Independent</Choice>
                    <Choice active={accountType === "institution"} onClick={() => setAccountType("institution")}>Institution</Choice>
                  </div>

                  <Field label="Full name" value={form.name || ""} onChange={(v) => set("name", v)} required />
                  <Field label="Email" type="email" value={form.email || ""} onChange={(v) => set("email", v)} required />
                  <Field label="Password" type="password" value={form.password || ""} onChange={(v) => set("password", v)} required />

                  {accountType === "institution" && (
                    <>
                      <div className="grid grid-cols-2 gap-2">
                        <Choice active={institutionMode === "join"} onClick={() => setInstitutionMode("join")}>Join</Choice>
                        <Choice active={institutionMode === "create"} onClick={() => setInstitutionMode("create")}>Create</Choice>
                      </div>

                      {institutionMode === "join" ? (
                        <>
                          <label className="block text-sm">
                            <span className="mb-2 block text-slate-400">I am a...</span>
                            <select value={form.role || "student"} onChange={(e) => set("role", e.target.value)} className="w-full rounded-xl border border-white/10 bg-[#07111f] px-4 py-3 text-white outline-none">
                              <option value="student">Student</option>
                              <option value="teacher">Teacher</option>
                            </select>
                          </label>
                          <Field label="Institution code" value={form.institutionCode || ""} onChange={(v) => set("institutionCode", v.toUpperCase())} required />
                        </>
                      ) : (
                        <>
                          <Field label="Institution name" value={form.institutionName || ""} onChange={(v) => set("institutionName", v)} required />
                          <Field label="Student seats (0 = unlimited)" type="number" value={form.maxStudents ?? 30} onChange={(v) => set("maxStudents", v)} />
                        </>
                      )}
                    </>
                  )}

                  <SubmitButton loading={loading}>Create account →</SubmitButton>
                </form>
              )}

              <button onClick={() => navigate("/")} className="mt-5 w-full text-center text-xs text-slate-600 hover:text-slate-300">
                ← Back to ENGiTwin
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({ label, type = "text", value, onChange, required }) {
  return (
    <label className="block text-sm">
      <span className="mb-2 block text-slate-400">{label}</span>
      <input required={required} type={type} value={value} onChange={(e) => onChange(e.target.value)} className="w-full rounded-xl border border-white/10 bg-[#07111f] px-4 py-3 text-white outline-none transition focus:border-cyan-400/50" />
    </label>
  );
}

function Choice({ active, onClick, children }) {
  return <button type="button" onClick={onClick} className={`rounded-xl border px-3 py-2.5 text-sm font-semibold ${active ? "border-cyan-400/30 bg-cyan-400/10 text-cyan-300" : "border-white/10 text-slate-500"}`}>{children}</button>;
}

function SubmitButton({ loading, children }) {
  return <button disabled={loading} className="w-full rounded-xl bg-cyan-400 py-3.5 font-bold text-slate-950 disabled:opacity-50">{loading ? "Please wait..." : children}</button>;
}