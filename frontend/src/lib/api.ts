import axios from "axios";

const BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000/api";

export async function uploadEvidence(file: File, onProgress?: (p: number) => void) {
  const form = new FormData();
  form.append("file", file);
  const res = await axios.post(`${BASE}/upload-evidence`, form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (e.total && onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
    },
  });
  return res.data;
}

export async function analyzeEvidence(file_id: string) {
  const form = new FormData();
  form.append("file_id", file_id);
  const res = await axios.post(`${BASE}/analyze`, form);
  return res.data;
}

export async function generateReport(file_id: string) {
  const form = new FormData();
  form.append("file_id", file_id);
  const res = await fetch(`${BASE}/report`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Report generation failed");
  return await res.blob();
}

export async function searchEntities(query: string) {
  const res = await axios.post(`${BASE}/cases/search`, { query });
  return res.data;
}

export async function getTopEntities() {
  const res = await axios.get(`${BASE}/cases/top-entities`);
  return res.data;
}

export async function getUnifiedSummary() {
  const res = await axios.get(`${BASE}/cases/summary`);
  return res.data;
}

