
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

export interface Question {
  id: QuestionID;
  text: string;
  difficulty: number;
  knowledge_unit_id: KnowledgeUnitID;
}

export interface StudySessionView {
  id: SessionID;
  questions: Question[];
  progress: number;
  max_questions: number;
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
  feedback?: string; // Optional field for AI explanation
}

export interface MasteryUpdateResponse {
  knowledge_unit_id: KnowledgeUnitID;
  mastery_level: number;
}
