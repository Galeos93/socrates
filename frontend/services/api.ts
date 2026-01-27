
import {
  IngestResponse,
  LearningPlanResponse,
  LearningPlanDetails,
  StartSessionResponse,
  StudySessionView,
  AssessmentResponse,
  MasteryUpdateResponse,
  AssessmentFeedbackResponse,
  QuestionFeedbackResponse
} from '../types';
import { withRelatedProject } from '@vercel/related-projects';

const apiHost = withRelatedProject({
  projectName: 'socrates-backend',
  /**
   * Specify a default host that will be used for the backend if the related project
   * data cannot be parsed or is missing (e.g., in local development).
   */
  defaultHost: process.env.BACKEND_HOST || 'http://localhost:8000',
});

// Ensure the URL has a protocol - withRelatedProject returns just hostname in production
const BASE_URL = apiHost.startsWith('http') ? apiHost : `https://${apiHost}`;

/**
 * Note: These calls assume the backend is running locally.
 * In a real-world scenario, you might have environment-specific URLs.
 */

export const api = {
  async ingestDocument(file: File): Promise<IngestResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${BASE_URL}/documents`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) throw new Error('Failed to ingest document');
    return response.json();
  },

  async createLearningPlan(documentIds: string[]): Promise<LearningPlanResponse> {
    const response = await fetch(`${BASE_URL}/learning-plans`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_ids: documentIds }),
    });

    if (!response.ok) throw new Error('Failed to create learning plan');
    return response.json();
  },

  async getLearningPlan(learningPlanId: string): Promise<LearningPlanDetails> {
    const response = await fetch(`${BASE_URL}/learning-plans/${learningPlanId}`);

    if (!response.ok) throw new Error('Failed to get learning plan');
    return response.json();
  },

  async startStudySession(learningPlanId: string): Promise<StartSessionResponse> {
    const response = await fetch(`${BASE_URL}/learning-plans/${learningPlanId}/sessions`, {
      method: 'POST'
    });

    if (!response.ok) throw new Error('Failed to start study session');
    return response.json();
  },

  async getStudySession(learningPlanId: string, sessionId: string): Promise<StudySessionView> {
    const response = await fetch(`${BASE_URL}/learning-plans/${learningPlanId}/sessions/${sessionId}`);

    if (!response.ok) throw new Error('Failed to fetch study session');
    return response.json();
  },

  async submitAnswer(learningPlanId: string, sessionId: string, questionId: string, userAnswer: string): Promise<{ status: string }> {
    const response = await fetch(`${BASE_URL}/learning-plans/${learningPlanId}/sessions/${sessionId}/answers/${questionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userAnswer), // Sending user answer in Body as requested
    });

    if (!response.ok) throw new Error('Failed to submit answer');
    return response.json();
  },

  async assessQuestion(
    learningPlanId: string,
    sessionId: string,
    questionId: string
  ): Promise<AssessmentResponse> {
    const response = await fetch(`${BASE_URL}/learning-plans/${learningPlanId}/sessions/${sessionId}/assess/${questionId}`, {
      method: 'POST'
    });

    if (!response.ok) throw new Error('Failed to assess question');
    return response.json();
  },

  async updateMastery(learningPlanId: string, kuId: string): Promise<MasteryUpdateResponse> {
    const response = await fetch(`${BASE_URL}/learning-plans/${learningPlanId}/knowledge-units/${kuId}/mastery`, {
      method: 'POST'
    });

    if (!response.ok) throw new Error('Failed to update mastery');
    return response.json();
  },

  async submitAssessmentFeedback(
    learningPlanId: string,
    sessionId: string,
    questionId: string,
    agrees: boolean,
    comment?: string
  ): Promise<AssessmentFeedbackResponse> {
    const response = await fetch(
      `${BASE_URL}/learning-plans/${learningPlanId}/sessions/${sessionId}/questions/${questionId}/assessments/feedback`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agrees, comment }),
      }
    );

    if (!response.ok) throw new Error('Failed to submit assessment feedback');
    return response.json();
  },

  async submitQuestionFeedback(
    learningPlanId: string,
    sessionId: string,
    questionId: string,
    isHelpful: boolean
  ): Promise<QuestionFeedbackResponse> {
    const response = await fetch(
      `${BASE_URL}/learning-plans/${learningPlanId}/sessions/${sessionId}/questions/${questionId}/feedback`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_helpful: isHelpful }),
      }
    );

    if (!response.ok) throw new Error('Failed to submit question feedback');
    return response.json();
  }
};