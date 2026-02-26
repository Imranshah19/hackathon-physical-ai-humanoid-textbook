/**
 * Hook for fetching personalized content (T047).
 *
 * Provides methods to fetch chapters, code examples, and exercises
 * with personalization based on user profile.
 */

import { useState, useCallback } from 'react';
import { config } from '../config';

// Types
export interface PersonalizationSettings {
  contentVariant: string;
  preferredLanguage: string;
  availableLanguages: string[];
  hardwareVariant: string;
  availableHardware: string[];
  showAdvancedTopics: boolean;
  showHardwareExercises: boolean;
}

export interface CodeExample {
  exampleId: string;
  title: string;
  description: string;
  languages: Record<string, string>;
  preferredLanguage: string;
  output?: string;
}

export interface Exercise {
  exerciseId: string;
  title: string;
  description: string;
  difficulty: string;
  hardwareVariant: string;
  instructions: string;
  hints: string[];
  solution?: string;
}

export interface ChapterContent {
  chapterId: string;
  title: string;
  variant: string;
  contentHtml: string;
  codeExamples: Array<{
    id: string;
    title: string;
    description: string;
    languages: Record<string, string>;
    preferred: string;
    output?: string;
  }>;
  exercises: Array<{
    id: string;
    title: string;
    description: string;
    difficulty: string;
    hardware_variant: string;
    instructions: string;
    hints: string[];
  }>;
  metadata: {
    preferredLanguage: string;
    hardwareVariant: string;
    showAdvanced: boolean;
    variantOverride?: boolean;
  };
}

export interface ContentPreferences {
  contentVariant: string;
  preferredLanguage: string;
  hardwareVariant: string;
  autoPersonalize: boolean;
}

interface UsePersonalizedContentReturn {
  // Settings
  settings: PersonalizationSettings | null;
  preferences: ContentPreferences | null;
  isLoadingSettings: boolean;

  // Content
  chapter: ChapterContent | null;
  codeExample: CodeExample | null;
  exercise: Exercise | null;
  isLoadingContent: boolean;
  contentError: string | null;

  // Actions
  fetchSettings: () => Promise<void>;
  fetchPreferences: () => Promise<void>;
  updatePreferences: (prefs: Partial<ContentPreferences>) => Promise<void>;
  fetchChapter: (chapterId: string, variantOverride?: string) => Promise<void>;
  fetchCodeExample: (exampleId: string, languageOverride?: string) => Promise<void>;
  fetchExercise: (exerciseId: string) => Promise<void>;
  clearContent: () => void;
}

const API_BASE = config.backendApiUrl;

export function usePersonalizedContent(): UsePersonalizedContentReturn {
  // Settings state
  const [settings, setSettings] = useState<PersonalizationSettings | null>(null);
  const [preferences, setPreferences] = useState<ContentPreferences | null>(null);
  const [isLoadingSettings, setIsLoadingSettings] = useState(false);

  // Content state
  const [chapter, setChapter] = useState<ChapterContent | null>(null);
  const [codeExample, setCodeExample] = useState<CodeExample | null>(null);
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [contentError, setContentError] = useState<string | null>(null);

  // Fetch personalization settings
  const fetchSettings = useCallback(async () => {
    setIsLoadingSettings(true);
    try {
      const response = await fetch(`${API_BASE}/api/content/settings`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch settings');
      }

      const data = await response.json();
      setSettings({
        contentVariant: data.content_variant,
        preferredLanguage: data.preferred_language,
        availableLanguages: data.available_languages,
        hardwareVariant: data.hardware_variant,
        availableHardware: data.available_hardware,
        showAdvancedTopics: data.show_advanced_topics,
        showHardwareExercises: data.show_hardware_exercises,
      });
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setIsLoadingSettings(false);
    }
  }, []);

  // Fetch user preferences
  const fetchPreferences = useCallback(async () => {
    setIsLoadingSettings(true);
    try {
      const response = await fetch(`${API_BASE}/api/content/preferences`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch preferences');
      }

      const data = await response.json();
      setPreferences({
        contentVariant: data.content_variant,
        preferredLanguage: data.preferred_language,
        hardwareVariant: data.hardware_variant,
        autoPersonalize: data.auto_personalize,
      });
    } catch (error) {
      console.error('Error fetching preferences:', error);
    } finally {
      setIsLoadingSettings(false);
    }
  }, []);

  // Update preferences
  const updatePreferences = useCallback(async (prefs: Partial<ContentPreferences>) => {
    try {
      const response = await fetch(`${API_BASE}/api/content/preferences`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          content_variant: prefs.contentVariant,
          preferred_language: prefs.preferredLanguage,
          hardware_variant: prefs.hardwareVariant,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update preferences');
      }

      const data = await response.json();
      setPreferences({
        contentVariant: data.content_variant,
        preferredLanguage: data.preferred_language,
        hardwareVariant: data.hardware_variant,
        autoPersonalize: data.auto_personalize,
      });
    } catch (error) {
      console.error('Error updating preferences:', error);
      throw error;
    }
  }, []);

  // Fetch chapter content
  const fetchChapter = useCallback(async (chapterId: string, variantOverride?: string) => {
    setIsLoadingContent(true);
    setContentError(null);

    try {
      const url = new URL(`${API_BASE}/api/content/chapter/${chapterId}`);
      if (variantOverride) {
        url.searchParams.set('variant', variantOverride);
      }

      const response = await fetch(url.toString(), {
        credentials: 'include',
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Chapter '${chapterId}' not found`);
        }
        throw new Error('Failed to fetch chapter');
      }

      const data = await response.json();
      setChapter({
        chapterId: data.chapter_id,
        title: data.title,
        variant: data.variant,
        contentHtml: data.content_html,
        codeExamples: data.code_examples,
        exercises: data.exercises,
        metadata: {
          preferredLanguage: data.metadata.preferred_language,
          hardwareVariant: data.metadata.hardware_variant,
          showAdvanced: data.metadata.show_advanced,
          variantOverride: data.metadata.variant_override,
        },
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setContentError(message);
      console.error('Error fetching chapter:', error);
    } finally {
      setIsLoadingContent(false);
    }
  }, []);

  // Fetch code example
  const fetchCodeExample = useCallback(async (exampleId: string, languageOverride?: string) => {
    setIsLoadingContent(true);
    setContentError(null);

    try {
      const url = new URL(`${API_BASE}/api/content/code-example/${exampleId}`);
      if (languageOverride) {
        url.searchParams.set('language', languageOverride);
      }

      const response = await fetch(url.toString(), {
        credentials: 'include',
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Code example '${exampleId}' not found`);
        }
        throw new Error('Failed to fetch code example');
      }

      const data = await response.json();
      setCodeExample({
        exampleId: data.example_id,
        title: data.title,
        description: data.description,
        languages: data.languages,
        preferredLanguage: data.preferred_language,
        output: data.output,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setContentError(message);
      console.error('Error fetching code example:', error);
    } finally {
      setIsLoadingContent(false);
    }
  }, []);

  // Fetch exercise
  const fetchExercise = useCallback(async (exerciseId: string) => {
    setIsLoadingContent(true);
    setContentError(null);

    try {
      const response = await fetch(`${API_BASE}/api/content/exercise/${exerciseId}`, {
        credentials: 'include',
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Exercise '${exerciseId}' not found`);
        }
        throw new Error('Failed to fetch exercise');
      }

      const data = await response.json();
      setExercise({
        exerciseId: data.exercise_id,
        title: data.title,
        description: data.description,
        difficulty: data.difficulty,
        hardwareVariant: data.hardware_variant,
        instructions: data.instructions,
        hints: data.hints,
        solution: data.solution,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setContentError(message);
      console.error('Error fetching exercise:', error);
    } finally {
      setIsLoadingContent(false);
    }
  }, []);

  // Clear content
  const clearContent = useCallback(() => {
    setChapter(null);
    setCodeExample(null);
    setExercise(null);
    setContentError(null);
  }, []);

  return {
    // Settings
    settings,
    preferences,
    isLoadingSettings,

    // Content
    chapter,
    codeExample,
    exercise,
    isLoadingContent,
    contentError,

    // Actions
    fetchSettings,
    fetchPreferences,
    updatePreferences,
    fetchChapter,
    fetchCodeExample,
    fetchExercise,
    clearContent,
  };
}

export default usePersonalizedContent;
