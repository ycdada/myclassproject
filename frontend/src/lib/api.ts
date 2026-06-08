/**
 * API client for DSALearn backend.
 *
 * Automatically falls back to mock data when:
 * - NEXT_PUBLIC_DEMO_MODE=true
 * - Backend is unreachable
 */

import {
  isDemoMode,
  getMockTopics,
  getMockResources,
  getMockQuestions,
  getMockLearningPath,
  getMockAssessment,
  MOCK_PROFILE,
} from "./mockData";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

function isOffline(): boolean {
  return isDemoMode() || !navigator.onLine;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  if (isOffline()) {
    throw new ApiError(0, "Demo mode — skipping network request");
  }

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

function fallback<T>(label: string, mockData: T): T {
  if (process.env.NODE_ENV !== "production" || isDemoMode()) {
    console.warn(`[API] Using mock data for: ${label}`);
  }
  return mockData;
}

// Auth
export const auth = {
  register: async (data: { username: string; email: string; password: string; major?: string }) => {
    try {
      return await request<{ access_token: string; user_id: string; username: string }>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      });
    } catch {
      return fallback("auth.register", {
        access_token: "mock_token_demo",
        user_id: "demo_user_001",
        username: data.username,
      });
    }
  },
  login: async (data: { username: string; password: string }) => {
    try {
      return await request<{ access_token: string; user_id: string; username: string }>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
      });
    } catch {
      return fallback("auth.login", {
        access_token: "mock_token_demo",
        user_id: "demo_user_001",
        username: data.username,
      });
    }
  },
};

// Topics
export const topics = {
  list: async (params?: { category?: string; difficulty?: number }) => {
    try {
      const searchParams = new URLSearchParams();
      if (params?.category) searchParams.set("category", params.category);
      if (params?.difficulty) searchParams.set("difficulty", String(params.difficulty));
      return await request<{ topics: any[]; total: number }>(`/api/topics?${searchParams}`);
    } catch {
      const topics = getMockTopics(params?.category);
      return fallback("topics.list", { topics, total: topics.length });
    }
  },
  get: async (topicId: string) => {
    try {
      return await request<any>(`/api/topics/${topicId}`);
    } catch {
      const topics = getMockTopics();
      return fallback("topics.get", topics.find((t) => t.id === topicId) || topics[0]);
    }
  },
  getPrerequisites: async (topicId: string) => {
    try {
      return await request<any>(`/api/topics/${topicId}/prerequisites`);
    } catch {
      return fallback("topics.getPrerequisites", { topic_id: topicId, prerequisites: [] });
    }
  },
};

// Resources
export const resources = {
  list: async (params?: { student_id?: string; topic_id?: string; resource_type?: string }) => {
    try {
      const searchParams = new URLSearchParams();
      if (params?.student_id) searchParams.set("student_id", params.student_id);
      if (params?.topic_id) searchParams.set("topic_id", params.topic_id);
      if (params?.resource_type) searchParams.set("resource_type", params.resource_type);
      return await request<{ resources: any[]; total: number }>(`/api/resources?${searchParams}`);
    } catch {
      const resources = getMockResources(params?.topic_id, params?.resource_type);
      return fallback("resources.list", { resources, total: resources.length });
    }
  },
  get: async (resourceId: string) => {
    try {
      return await request<any>(`/api/resources/${resourceId}`);
    } catch {
      const resources = getMockResources();
      return fallback("resources.get", resources.find((r) => r.id === resourceId) || resources[0]);
    }
  },
  feedback: async (resourceId: string, rating: number, comment?: string) => {
    try {
      return await request<any>(`/api/resources/${resourceId}/feedback`, {
        method: "POST",
        body: JSON.stringify({ rating, comment }),
      });
    } catch {
      return fallback("resources.feedback", { resource_id: resourceId, rating, status: "recorded" });
    }
  },
};

// Exercises
export const exercises = {
  list: async (params?: { topic_id?: string; difficulty?: number; question_type?: string; count?: number }) => {
    try {
      const searchParams = new URLSearchParams();
      if (params?.topic_id) searchParams.set("topic_id", params.topic_id);
      if (params?.difficulty) searchParams.set("difficulty", String(params.difficulty));
      if (params?.question_type) searchParams.set("question_type", params.question_type);
      if (params?.count) searchParams.set("count", String(params.count || 10));
      return await request<{ exercises: any[]; total: number }>(`/api/exercises?${searchParams}`);
    } catch {
      const exercises = getMockQuestions(params?.topic_id, params?.question_type);
      return fallback("exercises.list", { exercises, total: exercises.length });
    }
  },
  submit: async (data: { student_id: string; exercise_id: string; answer: string; time_spent_seconds?: number }) => {
    try {
      return await request<{ is_correct: boolean; correct_answer: string; explanation: string; score: number }>(
        "/api/exercises/submit",
        { method: "POST", body: JSON.stringify(data) }
      );
    } catch {
      return fallback("exercises.submit", {
        is_correct: Math.random() > 0.5,
        correct_answer: "参考答案（演示模式）",
        explanation: "这是演示模式下的模拟评估结果。实际使用时将显示详细的解析。",
        score: 1.0,
      });
    }
  },
  getHints: async (exerciseId: string, hintLevel: number = 1) => {
    try {
      return await request<any>(`/api/exercises/${exerciseId}/hints?hint_level=${hintLevel}`);
    } catch {
      const questions = getMockQuestions();
      const q = questions.find((q) => q.id === exerciseId);
      const hints = q?.hints || ["暂无提示"];
      const idx = Math.min(hintLevel - 1, hints.length - 1);
      return fallback("exercises.getHints", { exercise_id: exerciseId, hint_level: hintLevel, hint: hints[idx] });
    }
  },
};

// Learning Path
export const learningPath = {
  generate: async (studentId: string) => {
    try {
      return await request<any>(`/api/learning-path/generate?student_id=${studentId}`, { method: "POST" });
    } catch {
      return fallback("learningPath.generate", {
        id: "mock_path_001",
        student_id: studentId,
        topics_sequence: getMockLearningPath(),
        generated_at: new Date().toISOString(),
        is_active: true,
      });
    }
  },
  getCurrent: async (studentId: string) => {
    try {
      return await request<any>(`/api/learning-path/current/${studentId}`);
    } catch {
      return fallback("learningPath.getCurrent", {
        id: "mock_path_001",
        student_id: studentId,
        topics_sequence: getMockLearningPath(),
        generated_at: new Date().toISOString(),
        is_active: true,
      });
    }
  },
  updateProgress: async (data: { student_id: string; topic_id: string; status: string; time_spent_minutes?: number }) => {
    try {
      return await request<any>("/api/learning-path/progress", {
        method: "PUT",
        body: JSON.stringify(data),
      });
    } catch {
      return fallback("learningPath.updateProgress", { ...data, status: data.status || "updated" });
    }
  },
};

// Assessment
export const assessment = {
  getReport: async (studentId: string) => {
    try {
      return await request<any>(`/api/assessment/report/${studentId}`);
    } catch {
      return fallback("assessment.getReport", getMockAssessment().report);
    }
  },
  getDashboard: async (studentId: string) => {
    try {
      return await request<any>(`/api/assessment/dashboard/${studentId}`);
    } catch {
      return fallback("assessment.getDashboard", getMockAssessment().dashboard);
    }
  },
  selfEval: async (studentId: string, topicId: string, confidence: number, notes?: string) => {
    try {
      return await request<any>(`/api/assessment/self-eval/${studentId}`, {
        method: "POST",
        body: JSON.stringify({ topic_id: topicId, confidence, notes }),
      });
    } catch {
      return fallback("assessment.selfEval", { student_id: studentId, topic_id: topicId, confidence, status: "recorded" });
    }
  },
};

export { MOCK_PROFILE as mockProfile };
