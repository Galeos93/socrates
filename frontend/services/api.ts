
import { 
  IngestResponse, 
  LearningPlanResponse, 
  StartSessionResponse, 
  StudySessionView, 
  AssessmentResponse,
  MasteryUpdateResponse
} from '../types';

const BASE_URL = 'http://localhost:8000';

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

  async submitAnswer(learningPlanId: string, sessionId: string, questionId: string): Promise<{ status: string }> {
    // Fix: Changed 'question_id' to 'questionId' to match the function parameter name
    const response = await fetch(`${BASE_URL}/learning-plans/${learningPlanId}/sessions/${sessionId}/answers/${questionId}`, {
      method: 'POST'
    });
    
    if (!response.ok) throw new Error('Failed to submit answer');
    return response.json();
  },

  async assessQuestion(
    learningPlanId: string, 
    sessionId: string, 
    questionId: string, 
    userAnswer: string
  ): Promise<AssessmentResponse> {
    // Note: backend uses query parameter for user_answer
    const params = new URLSearchParams({ user_answer: userAnswer });
    const response = await fetch(`${BASE_URL}/learning-plans/${learningPlanId}/sessions/${sessionId}/assess/${questionId}?${params.toString()}`, {
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
  }
};