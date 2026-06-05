/**
 * API client for DSALearn backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(response.status, error);
  }

  return response.json();
}

// Auth
export const auth = {
  register: (data: { username: string; email: string; password: string; major?: string }) =>
    request<{ access_token: string; user_id: string; username: string }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  login: (data: { username: string; password: string }) =>
    request<{ access_token: string; user_id: string; username: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// Topics
export const topics = {
  list: (params?: { category?: string; difficulty?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set("category", params.category);
    if (params?.difficulty) searchParams.set("difficulty", String(params.difficulty));
    return request<{ topics: any[]; total: number }>(`/api/topics?${searchParams}`);
  },
  get: (topicId: string) => request<any>(`/api/topics/${topicId}`),
  getPrerequisites: (topicId: string) =>
    request<any>(`/api/topics/${topicId}/prerequisites`),
};

// Resources
export const resources = {
  list: (params?: { student_id?: string; topic_id?: string; resource_type?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.student_id) searchParams.set("student_id", params.student_id);
    if (params?.topic_id) searchParams.set("topic_id", params.topic_id);
    if (params?.resource_type) searchParams.set("resource_type", params.resource_type);
    return request<{ resources: any[]; total: number }>(`/api/resources?${searchParams}`);
  },
  get: (resourceId: string) => request<any>(`/api/resources/${resourceId}`),
  feedback: (resourceId: string, rating: number, comment?: string) =>
    request<any>(`/api/resources/${resourceId}/feedback`, {
      method: "POST",
      body: JSON.stringify({ rating, comment }),
    }),
};

// Exercises
export const exercises = {
  list: (params?: { topic_id?: string; difficulty?: number; question_type?: string; count?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.topic_id) searchParams.set("topic_id", params.topic_id);
    if (params?.difficulty) searchParams.set("difficulty", String(params.difficulty));
    if (params?.question_type) searchParams.set("question_type", params.question_type);
    if (params?.count) searchParams.set("count", String(params.count));
    return request<{ exercises: any[]; total: number }>(`/api/exercises?${searchParams}`);
  },
  submit: (data: { student_id: string; exercise_id: string; answer: string; time_spent_seconds?: number }) =>
    request<{ is_correct: boolean; correct_answer: string; explanation: string; score: number }>(
      "/api/exercises/submit",
      { method: "POST", body: JSON.stringify(data) }
    ),
  getHints: (exerciseId: string, hintLevel: number = 1) =>
    request<any>(`/api/exercises/${exerciseId}/hints?hint_level=${hintLevel}`),
};

// Learning Path
export const learningPath = {
  generate: (studentId: string) =>
    request<any>(`/api/learning-path/generate?student_id=${studentId}`, { method: "POST" }),
  getCurrent: (studentId: string) =>
    request<any>(`/api/learning-path/current/${studentId}`),
  updateProgress: (data: { student_id: string; topic_id: string; status: string; time_spent_minutes?: number }) =>
    request<any>("/api/learning-path/progress", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};

// Assessment
export const assessment = {
  getReport: (studentId: string) =>
    request<any>(`/api/assessment/report/${studentId}`),
  getDashboard: (studentId: string) =>
    request<any>(`/api/assessment/dashboard/${studentId}`),
  selfEval: (studentId: string, topicId: string, confidence: number, notes?: string) =>
    request<any>(`/api/assessment/self-eval/${studentId}`, {
      method: "POST",
      body: JSON.stringify({ topic_id: topicId, confidence, notes }),
    }),
};
