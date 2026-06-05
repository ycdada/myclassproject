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

interface StudentState {
  studentId: string | null;
  username: string | null;
  profile: StudentProfile | null;
  profileVersion: number;
  isLoggedIn: boolean;

  setAuth: (studentId: string, username: string, token: string) => void;
  setProfile: (profile: StudentProfile, version: number) => void;
  updateProfileDimension: (dimension: string, value: any) => void;
  logout: () => void;
}

export const useStudentStore = create<StudentState>((set, get) => ({
  studentId: null,
  username: null,
  profile: null,
  profileVersion: 0,
  isLoggedIn: false,

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

  logout: () => {
    localStorage.removeItem("token");
    set({
      studentId: null,
      username: null,
      profile: null,
      profileVersion: 0,
      isLoggedIn: false,
    });
  },
}));
