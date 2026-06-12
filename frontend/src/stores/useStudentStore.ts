"use client";

import { create } from "zustand";

interface StudentProfile {
  knowledge_foundation: Record<string, number>;
  cognitive_style: string;
  error_prone_areas: string[];
  learning_pace: number;
  preferred_resource_types: string[];
  motivation_level: string;
  attention_span: string;
  goal: string;
}

interface GeneratedResource {
  id: string;
  topic_id: string;
  resource_type: string;
  title: string;
  content?: string;
  mindmap?: string;
  questions?: any[];
  hints?: string[];
  solution?: string;
  test_cases?: any[];
  verification?: any;
  quality?: any;
  created_at?: string;
}

interface StudentState {
  studentId: string | null;
  username: string | null;
  profile: StudentProfile | null;
  profileVersion: number;
  isLoggedIn: boolean;

  // Session-generated resources (shared across chat & resources pages)
  sessionResources: GeneratedResource[];

  setAuth: (studentId: string, username: string, token: string) => void;
  setProfile: (profile: StudentProfile, version: number) => void;
  updateProfileDimension: (dimension: string, value: any) => void;
  addSessionResource: (resource: GeneratedResource) => void;
  addSessionResources: (resources: GeneratedResource[]) => void;
  clearSessionResources: () => void;
  logout: () => void;
}

export const useStudentStore = create<StudentState>((set, get) => ({
  studentId: null,
  username: null,
  profile: null,
  profileVersion: 0,
  isLoggedIn: false,
  sessionResources: [],

  setAuth: (studentId, username, token) => {
    localStorage.setItem("token", token);
    set({ studentId, username, isLoggedIn: true });
  },

  setProfile: (profile, version) => {
    set({ profile, profileVersion: version });
  },

  updateProfileDimension: (dimension, value) => {
    const current = get().profile;
    if (!current) return;
    set({
      profile: { ...current, [dimension]: value },
      profileVersion: get().profileVersion + 1,
    });
  },

  addSessionResource: (resource) => {
    const existing = get().sessionResources;
    // Avoid duplicates
    if (existing.find((r) => r.id === resource.id)) return;
    set({ sessionResources: [...existing, { ...resource, created_at: new Date().toISOString() }] });
  },

  addSessionResources: (resources) => {
    const existing = get().sessionResources;
    const existingIds = new Set(existing.map((r) => r.id));
    const newOnes = resources.filter((r) => !existingIds.has(r.id)).map((r) => ({ ...r, created_at: new Date().toISOString() }));
    if (newOnes.length > 0) set({ sessionResources: [...existing, ...newOnes] });
  },

  clearSessionResources: () => set({ sessionResources: [] }),

  logout: () => {
    localStorage.removeItem("token");
    set({
      studentId: null, username: null, profile: null,
      profileVersion: 0, isLoggedIn: false, sessionResources: [],
    });
  },
}));
