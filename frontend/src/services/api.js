const API_BASE = "/api";

export const StorageKeys = {
  API_KEYS: "veriai_user_api_keys",
};

export function getStoredApiKeys() {
  try {
    const raw = localStorage.getItem(StorageKeys.API_KEYS);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function saveStoredApiKeys(keys) {
  try {
    localStorage.setItem(StorageKeys.API_KEYS, JSON.stringify(keys));
  } catch (e) {
    console.error("Failed to save keys locally", e);
  }
}

export function clearStoredApiKeys() {
  localStorage.removeItem(StorageKeys.API_KEYS);
}

export async function executeResearch({ question, mode = "deep", providers, allow_demo_fallback = true }) {
  const userKeys = getStoredApiKeys();
  const headers = {
    "Content-Type": "application/json",
  };

  // Pass user keys in custom headers
  if (userKeys.gemini) headers["x-gemini-api-key"] = userKeys.gemini;
  if (userKeys.openai) headers["x-openai-api-key"] = userKeys.openai;
  if (userKeys.anthropic) headers["x-anthropic-api-key"] = userKeys.anthropic;
  if (userKeys.groq) headers["x-groq-api-key"] = userKeys.groq;

  const res = await fetch(`${API_BASE}/research`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      question,
      mode,
      providers,
      api_keys: userKeys,
      allow_demo_fallback,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Research request failed" }));
    throw new Error(errorData.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}

export async function fetchProvidersStatus() {
  const res = await fetch(`${API_BASE}/providers/status`);
  if (!res.ok) throw new Error("Failed to fetch provider status");
  return await res.json();
}

export async function testProviderKey(providerId, apiKey) {
  const res = await fetch(`${API_BASE}/providers/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider_id: providerId, api_key: apiKey }),
  });
  if (!res.ok) throw new Error("Test connection failed");
  return await res.json();
}

export async function runEvaluationSuite() {
  const res = await fetch(`${API_BASE}/eval/run`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Evaluation suite run failed");
  return await res.json();
}

export async function verifyDocument(file, question) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("question", question);

  const res = await fetch(`${API_BASE}/documents/verify`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Document verification failed" }));
    throw new Error(err.detail || "Document verification failed");
  }

  return await res.json();
}
