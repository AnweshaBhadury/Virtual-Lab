const API_BASE = (
  import.meta.env.VITE_API_BASE || "http://localhost:8000"
).replace(/\/$/, "");

export class APIError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.status = status;
  }
}

export function getToken() {
  return localStorage.getItem("engitwin_token");
}

export function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem("engitwin_user") || "null");
  } catch {
    return null;
  }
}

export function saveAuth(data) {
  localStorage.setItem("engitwin_token", data.access_token);
  localStorage.setItem("engitwin_user", JSON.stringify(data.user));
}

export function clearAuth() {
  localStorage.removeItem("engitwin_token");
  localStorage.removeItem("engitwin_user");
}

async function request(path, options = {}) {
  const token = getToken();

  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  let response;

  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new APIError(
      `Cannot reach ENGiTwin backend at ${API_BASE}. Please try again later.`
    );
  }

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const detail = data?.detail || data?.message || response.statusText;
    throw new APIError(`${response.status}: ${detail}`, response.status);
  }

  return data;
}

export const api = {
  login: (email, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  signup: (name, email, password, role, institution_code = null) =>
    request("/auth/signup", {
      method: "POST",
      body: JSON.stringify({
        name,
        email,
        password,
        role,
        institution_code,
      }),
    }),

  me: () => request("/users/me"),

  labs: () => request("/labs"),

  createLab: (title, description, category) =>
    request("/labs", {
      method: "POST",
      body: JSON.stringify({ title, description, category }),
    }),

  experiments: (labId) => request(`/labs/${labId}/experiments`),

  experiment: (id) => request(`/experiments/${id}`),

  createExperiment: (
    labId,
    title,
    description,
    simulation_config,
    max_score
  ) =>
    request("/experiments", {
      method: "POST",
      body: JSON.stringify({
        lab_id: labId,
        title,
        description,
        simulation_config,
        max_score,
      }),
    }),

  startAttempt: (experiment_id) =>
    request("/attempts/start", {
      method: "POST",
      body: JSON.stringify({ experiment_id }),
    }),

  updateAttempt: (attemptId, simulation_data) =>
    request(`/attempts/${attemptId}`, {
      method: "PATCH",
      body: JSON.stringify({ simulation_data }),
    }),

  completeAttempt: (attemptId, measurements) =>
    request(`/attempts/${attemptId}/complete`, {
      method: "POST",
      body: JSON.stringify({ measurements }),
    }),

  attempts: () => request("/attempts/mine"),

  aiHistory: (attemptId) =>
    request(`/ai/attempts/${attemptId}/history`),

  aiAsk: (attemptId, student_message = null) =>
    request("/ai/ask", {
      method: "POST",
      body: JSON.stringify({
        attempt_id: attemptId,
        student_message,
      }),
    }),

  users: () => request("/users"),

  assignments: () => request("/assignments/mine"),

  createAssignment: (
    experiment_id,
    student_id,
    due_date = null
  ) =>
    request("/assignments", {
      method: "POST",
      body: JSON.stringify({
        experiment_id,
        student_id,
        due_date,
      }),
    }),

  analytics: () => request("/analytics/me"),

  institutions: () => request("/institutions"),

  createInstitution: (name, max_students = 0) =>
    request("/institutions", {
      method: "POST",
      body: JSON.stringify({
        name,
        max_students,
      }),
    }),
};