
export type DocumentID = string;
export type LearningPlanID = string;
export type SessionID = string;
export type QuestionID = string;
export type KnowledgeUnitID = string;

export interface Document {
  id: DocumentID;
  text: string;
  metadata: Record<string, any>;
}

export interface IngestResponse {
  document_id: DocumentID;
  filename: string;
  message: string;
}

export interface LearningPlanResponse {
  learning_plan_id: LearningPlanID;
  knowledge_unit_count: number;
  created_at: string;
}

export interface IncompleteSession {
  session_id: SessionID;
  questions_answered: number;
  total_questions: number;
  max_questions: number;
  started_at: string;
}

export interface LearningPlanSummary {
  learning_plan_id: LearningPlanID;
  knowledge_unit_count: number;
  average_mastery: number;
  created_at: string;
  completed_at: string | null;
  session_count: number;
  incomplete_sessions: IncompleteSession[];
}

export interface LearningPlanDetails {
  learning_plan_id: LearningPlanID;
  knowledge_unit_count: number;
  average_mastery: number;
  created_at: string;
  completed_at: string | null;
}

export interface Question {
  id: QuestionID;
  text: string;
  difficulty: number;
  knowledge_unit_id: KnowledgeUnitID;
  correct_answer?: string;
  user_answer?: string;  // Track if question was already answered
  is_correct?: boolean;  // Track if answer was assessed as correct
}

export interface StudySessionView {
  id: SessionID;
  questions: Question[];
  progress: number;
  max_questions: number;
  is_completed?: boolean;
}

export interface StartSessionResponse {
  session_id: SessionID;
  max_questions: number;
  question_count: number;
  started_at: string;
}

export interface AssessmentResponse {
  is_correct: boolean;
  question_id: QuestionID;
  correct_answer?: string;
  explanation?: string;
  feedback?: string; // Kept for backward compatibility if needed
}

export interface MasteryUpdateResponse {
  knowledge_unit_id: KnowledgeUnitID;
  mastery_level: number;
}

export interface AssessmentFeedbackResponse {
  feedback_id: string;
  question_id: QuestionID;
  score: number;
  message: string;
}

export interface QuestionFeedbackResponse {
  feedback_id: string;
  question_id: QuestionID;
  is_helpful: boolean;
  message: string;
}
