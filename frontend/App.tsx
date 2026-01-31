
import React, { useState, useEffect } from 'react';
import { Home, BookOpen, Brain, CheckCircle, ChevronRight, Upload, Loader2, Sparkles, BookText, BarChart2, ThumbsUp, ThumbsDown, MessageSquare, ArrowLeft, PlayCircle, PlusCircle, Clock, FolderOpen } from 'lucide-react';
import { api } from './services/api';
import { StudySessionView, Question, AssessmentResponse, LearningPlanDetails, LearningPlanSummary } from './types';
import { geminiService } from './services/geminiService';

// --- Sub-components ---

type AppView = 'home' | 'upload' | 'plan' | 'study';

const StepIndicator = ({ currentStep }: { currentStep: number }) => {
  const steps = ["Upload", "Plan", "Study"];
  return (
    <div className="flex items-center justify-center space-x-4 mb-8">
      {steps.map((label, idx) => (
        <React.Fragment key={label}>
          <div className="flex items-center space-x-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${currentStep >= idx ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-500'}`}>
              {idx + 1}
            </div>
            <span className={`text-sm ${currentStep >= idx ? 'text-indigo-900 font-semibold' : 'text-slate-400'}`}>{label}</span>
          </div>
          {idx < steps.length - 1 && <div className="w-12 h-px bg-slate-300" />}
        </React.Fragment>
      ))}
    </div>
  );
};

const Header = ({ onHomeClick, showHomeButton }: { onHomeClick?: () => void; showHomeButton?: boolean }) => (
  <header className="py-6 border-b border-slate-200 glass sticky top-0 z-50">
    <div className="container mx-auto px-4 flex justify-between items-center">
      <div className="flex items-center space-x-4">
        {showHomeButton && onHomeClick && (
          <button
            onClick={onHomeClick}
            className="p-2 rounded-lg hover:bg-slate-100 text-slate-600 transition-colors"
            title="Back to Home"
          >
            <ArrowLeft size={20} />
          </button>
        )}
        <div className="flex items-center space-x-2 cursor-pointer" onClick={onHomeClick}>
          <div className="bg-indigo-600 p-2 rounded-lg text-white">
            <Brain size={24} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 serif">Socrates</h1>
        </div>
      </div>
    </div>
  </header>
);

// --- Main Views ---

const App: React.FC = () => {
  const [view, setView] = useState<AppView>('home');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Home view state
  const [learningPlans, setLearningPlans] = useState<LearningPlanSummary[]>([]);
  const [loadingPlans, setLoadingPlans] = useState(true);

  // App State
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [learningPlanId, setLearningPlanId] = useState<string | null>(null);
  const [learningPlanDetails, setLearningPlanDetails] = useState<LearningPlanDetails | null>(null);
  const [session, setSession] = useState<StudySessionView | null>(null);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [answer, setAnswer] = useState('');
  const [assessment, setAssessment] = useState<AssessmentResponse | null>(null);
  const [hint, setHint] = useState<string | null>(null);

  // Feedback state
  const [questionFeedbackGiven, setQuestionFeedbackGiven] = useState(false);
  const [assessmentFeedbackGiven, setAssessmentFeedbackGiven] = useState(false);
  const [showAssessmentComment, setShowAssessmentComment] = useState(false);
  const [assessmentComment, setAssessmentComment] = useState('');

  // Load learning plans on mount
  useEffect(() => {
    loadLearningPlans();
  }, []);

  const loadLearningPlans = async () => {
    setLoadingPlans(true);
    try {
      const plans = await api.listLearningPlans();
      setLearningPlans(plans);
    } catch (err) {
      console.error('Failed to load learning plans:', err);
    } finally {
      setLoadingPlans(false);
    }
  };

  const goHome = () => {
    setView('home');
    setError(null);
    loadLearningPlans();
  };

  const selectLearningPlan = async (plan: LearningPlanSummary) => {
    setLoading(true);
    setError(null);
    try {
      setLearningPlanId(plan.learning_plan_id);
      const planDetails = await api.getLearningPlan(plan.learning_plan_id);
      setLearningPlanDetails(planDetails);
      setView('plan');
    } catch (err) {
      setError("Failed to load learning plan details.");
    } finally {
      setLoading(false);
    }
  };

  const continueSession = async (plan: LearningPlanSummary, sessionId: string) => {
    setLoading(true);
    setError(null);
    try {
      setLearningPlanId(plan.learning_plan_id);
      const planDetails = await api.getLearningPlan(plan.learning_plan_id);
      setLearningPlanDetails(planDetails);

      const sessionData = await api.getStudySession(plan.learning_plan_id, sessionId);
      setSession(sessionData);

      // Find the first unanswered question
      const firstUnansweredIdx = sessionData.questions.findIndex(q => !q.user_answer);
      setCurrentQuestionIdx(firstUnansweredIdx >= 0 ? firstUnansweredIdx : 0);

      setAnswer('');
      setAssessment(null);
      setHint(null);
      setView('study');
    } catch (err) {
      setError("Failed to continue session.");
    } finally {
      setLoading(false);
    }
  };
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    try {
      const res = await api.ingestDocument(file);
      setDocumentId(res.document_id);

      // Immediately create a learning plan for simplicity in this flow
      const planRes = await api.createLearningPlan([res.document_id]);
      setLearningPlanId(planRes.learning_plan_id);

      // Fetch the full learning plan details with mastery
      const planDetails = await api.getLearningPlan(planRes.learning_plan_id);
      setLearningPlanDetails(planDetails);

      setView('plan');
    } catch (err) {
      setError("Failed to process document. Ensure the backend is running");
    } finally {
      setLoading(false);
    }
  };

  const startSession = async () => {
    if (!learningPlanId) return;
    setLoading(true);
    try {
      const res = await api.startStudySession(learningPlanId);
      const sessionData = await api.getStudySession(learningPlanId, res.session_id);
      setSession(sessionData);
      setView('study');
      setCurrentQuestionIdx(0);
      setAnswer('');
      setAssessment(null);
      setHint(null);
    } catch (err) {
      setError("Failed to start study session.");
    } finally {
      setLoading(false);
    }
  };

  const submitAndAssess = async () => {
    if (!session || !learningPlanId) return;
    const q = session.questions[currentQuestionIdx];

    setLoading(true);
    try {
      // 1. Submit answer with the user content in body
      await api.submitAnswer(learningPlanId, session.id, q.id, answer);

      // 2. Assess the question (server already has the answer)
      const res = await api.assessQuestion(learningPlanId, session.id, q.id);
      setAssessment(res);

      // Update mastery in background
      await api.updateMastery(learningPlanId, q.knowledge_unit_id);

      // Refresh learning plan details to get updated mastery
      const planDetails = await api.getLearningPlan(learningPlanId);
      setLearningPlanDetails(planDetails);
    } catch (err) {
      setError("Failed to assess answer.");
    } finally {
      setLoading(false);
    }
  };

  const nextQuestion = () => {
    if (!session) return;

    if (currentQuestionIdx < session.questions.length - 1) {
      setCurrentQuestionIdx(prev => prev + 1);
      setAnswer('');
      setAssessment(null);
      setHint(null);
      setQuestionFeedbackGiven(false);
      setAssessmentFeedbackGiven(false);
      setShowAssessmentComment(false);
      setAssessmentComment('');
    } else {
      // Completed session - go back to plan summary
      setView('plan');
    }
  };

  const getHint = async () => {
    if (!session) return;
    const q = session.questions[currentQuestionIdx];
    setLoading(true);
    const h = await geminiService.getSocraticHint(q.text, undefined, q.correct_answer);
    setHint(h);
    setLoading(false);
  };

  const handleQuestionFeedback = async (isHelpful: boolean) => {
    if (!session || !learningPlanId || questionFeedbackGiven) return;
    const q = session.questions[currentQuestionIdx];

    try {
      await api.submitQuestionFeedback(learningPlanId, session.id, q.id, isHelpful);
      setQuestionFeedbackGiven(true);
    } catch (err) {
      console.error('Failed to submit question feedback:', err);
    }
  };

  const handleAssessmentFeedback = async (agrees: boolean) => {
    if (!session || !learningPlanId || !assessment || assessmentFeedbackGiven) return;

    try {
      await api.submitAssessmentFeedback(
        learningPlanId,
        session.id,
        assessment.question_id,
        agrees,
        assessmentComment || undefined
      );
      setAssessmentFeedbackGiven(true);
      setShowAssessmentComment(false);
      setAssessmentComment('');
    } catch (err) {
      console.error('Failed to submit assessment feedback:', err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header onHomeClick={goHome} showHomeButton={view !== 'home'} />

      <main className="flex-grow container mx-auto px-4 py-12 max-w-4xl">
        {view !== 'home' && <StepIndicator currentStep={view === 'upload' ? 0 : view === 'plan' ? 1 : 2} />}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 flex items-center space-x-3">
            <span className="font-bold">Error:</span>
            <span>{error}</span>
          </div>
        )}

        {/* HOME VIEW */}
        {view === 'home' && (
          <div className="space-y-8 animate-in fade-in duration-700">
            <div className="text-center space-y-4">
              <h2 className="text-4xl font-bold text-slate-900 serif">Welcome Back</h2>
              <p className="text-xl text-slate-500 max-w-2xl mx-auto">
                Continue your learning journey or start mastering new material.
              </p>
            </div>

            {/* Create New Learning Plan Button */}
            <div className="flex justify-center">
              <button
                onClick={() => setView('upload')}
                className="flex items-center space-x-3 px-6 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-2xl transition-all shadow-lg shadow-indigo-200"
              >
                <PlusCircle size={24} />
                <span>New Learning Plan</span>
              </button>
            </div>

            {/* Existing Learning Plans */}
            <div className="space-y-4">
              <h3 className="text-xl font-bold text-slate-800 flex items-center space-x-2">
                <FolderOpen size={24} className="text-slate-600" />
                <span>Your Learning Plans</span>
              </h3>

              {loadingPlans ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
                </div>
              ) : learningPlans.length === 0 ? (
                <div className="text-center py-12 bg-slate-50 rounded-2xl border border-slate-200">
                  <BookOpen className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                  <p className="text-slate-600 font-medium">No learning plans yet</p>
                  <p className="text-slate-400 text-sm mt-1">Upload a document to get started</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {learningPlans.map((plan) => (
                    <div
                      key={plan.learning_plan_id}
                      className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-grow">
                          <div className="flex items-center space-x-3 mb-3">
                            <span className="text-sm text-slate-500">
                              Created {new Date(plan.created_at).toLocaleDateString()}
                            </span>
                            <span className="text-slate-300">•</span>
                            <span className="text-sm text-slate-500">
                              {plan.knowledge_unit_count} knowledge units
                            </span>
                            <span className="text-slate-300">•</span>
                            <span className="text-sm text-slate-500">
                              {plan.session_count} session{plan.session_count !== 1 ? 's' : ''}
                            </span>
                          </div>

                          {/* Mastery Progress */}
                          <div className="flex items-center space-x-4 mb-4">
                            <div className="flex-grow h-3 bg-slate-100 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-indigo-600 rounded-full transition-all duration-500"
                                style={{ width: `${plan.average_mastery * 100}%` }}
                              />
                            </div>
                            <span className="text-lg font-bold text-slate-700">
                              {Math.round(plan.average_mastery * 100)}%
                            </span>
                          </div>

                          {/* Incomplete Sessions */}
                          {plan.incomplete_sessions.length > 0 && (
                            <div className="mb-4">
                              {plan.incomplete_sessions.map((incSession) => (
                                <button
                                  key={incSession.session_id}
                                  onClick={() => continueSession(plan, incSession.session_id)}
                                  disabled={loading}
                                  className="flex items-center space-x-2 px-4 py-2 bg-amber-50 hover:bg-amber-100 text-amber-700 rounded-xl text-sm font-medium transition-colors border border-amber-200"
                                >
                                  <Clock size={16} />
                                  <span>
                                    Continue session ({incSession.questions_answered}/{incSession.total_questions} questions answered)
                                  </span>
                                  <ChevronRight size={16} />
                                </button>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Actions */}
                        <div className="flex space-x-3 ml-4">
                          <button
                            onClick={() => selectLearningPlan(plan)}
                            disabled={loading}
                            className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition-colors"
                          >
                            <PlayCircle size={18} />
                            <span>{plan.session_count === 0 ? 'Start Learning' : 'New Session'}</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left mt-12">
              <FeatureCard
                icon={<BookText className="text-indigo-500" />}
                title="Claim Extraction"
                desc="Socrates identifies atomic statements verifiable within your text."
              />
              <FeatureCard
                icon={<Sparkles className="text-emerald-500" />}
                title="Skill Application"
                desc="Go beyond comprehension by testing your ability to apply knowledge."
              />
              <FeatureCard
                icon={<BarChart2 className="text-amber-500" />}
                title="Mastery Tracking"
                desc="Track your progress with a dynamic model of your understanding."
              />
            </div>
          </div>
        )}

        {/* UPLOAD VIEW */}
        {view === 'upload' && (
          <div className="text-center space-y-8 animate-in fade-in duration-700">
            <div className="space-y-4">
              <h2 className="text-4xl font-bold text-slate-900 serif">Deepen Your Knowledge</h2>
              <p className="text-xl text-slate-500 max-w-2xl mx-auto">
                Socrates reads your documents, extracts the core claims, and challenges you to apply what you've learned.
              </p>
            </div>

            <div className="relative group max-w-lg mx-auto">
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-slate-300 rounded-3xl cursor-pointer bg-white hover:bg-slate-50 hover:border-indigo-400 transition-all duration-300">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <div className="bg-indigo-50 p-4 rounded-2xl mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Upload className="w-8 h-8 text-indigo-600" />
                  </div>
                  <p className="mb-2 text-lg font-semibold text-slate-700">Drop your study material here</p>
                  <p className="text-sm text-slate-400">PDF Document (Max 10MB)</p>
                </div>
                <input type="file" className="hidden" accept=".pdf,.txt,.doc,.docx" onChange={handleFileUpload} disabled={loading} />
              </label>
              {loading && (
                <div className="absolute inset-0 bg-white/80 rounded-3xl flex flex-col items-center justify-center space-y-4">
                  <Loader2 className="w-12 h-12 text-indigo-600 animate-spin" />
                  <p className="font-medium text-slate-600">Analyzing knowledge units...</p>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left mt-12">
              <FeatureCard
                icon={<BookText className="text-indigo-500" />}
                title="Claim Extraction"
                desc="Socrates identifies atomic statements verifiable within your text."
              />
              <FeatureCard
                icon={<Sparkles className="text-emerald-500" />}
                title="Skill Application"
                desc="Go beyond comprehension by testing your ability to apply knowledge."
              />
              <FeatureCard
                icon={<BarChart2 className="text-amber-500" />}
                title="Mastery Tracking"
                desc="Track your progress with a dynamic model of your understanding."
              />
            </div>
          </div>
        )}

        {/* PLAN SUMMARY VIEW */}
        {view === 'plan' && (
          <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 p-8 border border-slate-100 animate-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-start mb-8">
              <div>
                <h2 className="text-3xl font-bold serif mb-2">Learning Plan Ready</h2>
                <p className="text-slate-500">We've structured your document into mastery-based units.</p>
              </div>
              <div className="bg-emerald-50 text-emerald-700 px-4 py-2 rounded-full text-sm font-bold flex items-center space-x-2">
                <CheckCircle size={16} />
                <span>Knowledge Mapped</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
              <div className="p-6 bg-slate-50 rounded-2xl">
                <p className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Knowledge Units</p>
                <p className="text-4xl font-bold text-slate-900">{learningPlanDetails?.knowledge_unit_count || 0}</p>
                <p className="text-sm text-slate-500 mt-1">Identified from document</p>
              </div>
              <div className="p-6 bg-slate-50 rounded-2xl">
                <p className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Current Mastery</p>
                <p className="text-4xl font-bold text-slate-900">
                  {learningPlanDetails ? Math.round(learningPlanDetails.average_mastery * 100) : 0}%
                </p>
                <div className="w-full h-2 bg-slate-200 rounded-full mt-3">
                  <div
                    className="h-full bg-indigo-600 rounded-full transition-all duration-500"
                    style={{ width: `${learningPlanDetails ? learningPlanDetails.average_mastery * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>

            <button
              onClick={startSession}
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-2xl transition-all flex items-center justify-center space-x-2 shadow-lg shadow-indigo-200"
            >
              {loading ? <Loader2 className="animate-spin" /> : (
                <>
                  <span>Begin Study Session</span>
                  <ChevronRight size={20} />
                </>
              )}
            </button>
          </div>
        )}

        {/* STUDY SESSION VIEW */}
        {view === 'study' && session && (
          <div className="space-y-6 animate-in fade-in duration-500">
            {/* Progress Bar */}
            <div className="flex items-center space-x-4">
              <div className="flex-grow bg-slate-200 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-indigo-600 h-full transition-all duration-500"
                  style={{ width: `${(currentQuestionIdx / session.questions.length) * 100}%` }}
                />
              </div>
              <span className="text-sm font-bold text-slate-500">
                {currentQuestionIdx + 1} of {session.questions.length}
              </span>
            </div>

            {/* Question Card */}
            <div className="bg-white rounded-3xl shadow-xl p-8 border border-slate-100 space-y-8">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs font-bold uppercase tracking-widest">
                    Question {currentQuestionIdx + 1}
                  </span>
                  <span className={`px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-widest ${
                    session.questions[currentQuestionIdx].difficulty >= 4 ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-600'
                  }`}>
                    Difficulty Level {session.questions[currentQuestionIdx].difficulty}
                  </span>
                </div>
                <h3 className="text-2xl font-bold text-slate-900 leading-tight">
                  {session.questions[currentQuestionIdx].text}
                </h3>

                {/* Question Feedback */}
                {!assessment && (
                  <div className="flex items-center space-x-3 pt-3">
                    <span className="text-sm text-slate-500">Is this question helpful?</span>
                    <button
                      onClick={() => handleQuestionFeedback(true)}
                      disabled={questionFeedbackGiven}
                      className={`p-2 rounded-lg transition-all ${
                        questionFeedbackGiven
                          ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                          : 'hover:bg-emerald-50 text-slate-400 hover:text-emerald-600'
                      }`}
                    >
                      <ThumbsUp size={18} />
                    </button>
                    <button
                      onClick={() => handleQuestionFeedback(false)}
                      disabled={questionFeedbackGiven}
                      className={`p-2 rounded-lg transition-all ${
                        questionFeedbackGiven
                          ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                          : 'hover:bg-red-50 text-slate-400 hover:text-red-600'
                      }`}
                    >
                      <ThumbsDown size={18} />
                    </button>
                    {questionFeedbackGiven && (
                      <span className="text-xs text-emerald-600 font-medium">Thanks for your feedback!</span>
                    )}
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <textarea
                  className="w-full min-h-[160px] p-6 rounded-2xl border-2 border-slate-100 focus:border-indigo-400 focus:outline-none transition-colors text-lg"
                  placeholder="Type your answer here..."
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  disabled={!!assessment}
                />

                {!assessment ? (
                  <div className="flex space-x-4">
                    <button
                      onClick={submitAndAssess}
                      disabled={loading || !answer.trim()}
                      className="flex-grow bg-slate-900 hover:bg-slate-800 text-white font-bold py-4 rounded-2xl transition-all"
                    >
                      {loading ? <Loader2 className="animate-spin mx-auto" /> : "Check Answer"}
                    </button>
                    <button
                      onClick={getHint}
                      disabled={loading}
                      className="px-6 border-2 border-slate-200 hover:bg-slate-50 text-slate-600 font-bold py-4 rounded-2xl transition-all flex items-center space-x-2"
                    >
                      <Sparkles size={18} />
                      <span>Hint</span>
                    </button>
                  </div>
                ) : (
                  <div className={`p-6 rounded-2xl border ${assessment.is_correct ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-200'} animate-in zoom-in-95 duration-300`}>
                    <div className="flex items-start space-x-4">
                      <div className={`p-2 rounded-full ${assessment.is_correct ? 'bg-emerald-200 text-emerald-800' : 'bg-red-200 text-red-800'}`}>
                        {assessment.is_correct ? <CheckCircle size={24} /> : <Loader2 size={24} className="rotate-45" />}
                      </div>
                      <div className="space-y-2">
                        <p className={`text-xl font-bold ${assessment.is_correct ? 'text-emerald-900' : 'text-red-900'}`}>
                          {assessment.is_correct ? "Correct!" : "Not quite right."}
                        </p>
                        <p className="text-slate-600 leading-relaxed">
                          {assessment.explanation || assessment.feedback || (assessment.is_correct ? "You demonstrated clear understanding of the knowledge unit." : "Try revisiting the section about this concept.")}
                        </p>
                        {!assessment.is_correct && assessment.correct_answer && (
                          <div className="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                            <p className="text-sm font-semibold text-slate-700 mb-1">Correct answer:</p>
                            <p className="text-slate-900">{assessment.correct_answer}</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Assessment Feedback */}
                    <div className="mt-6 p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
                      <div className="flex items-center space-x-2">
                        <MessageSquare size={16} className="text-slate-400" />
                        <span className="text-sm font-medium text-slate-700">Do you agree with this assessment?</span>
                      </div>

                      {!assessmentFeedbackGiven ? (
                        <div className="space-y-3">
                          <div className="flex space-x-3">
                            <button
                              onClick={() => handleAssessmentFeedback(true)}
                              className="flex-1 py-2 px-4 bg-emerald-100 hover:bg-emerald-200 text-emerald-700 rounded-lg font-medium transition-all"
                            >
                              Yes, I agree
                            </button>
                            <button
                              onClick={() => setShowAssessmentComment(true)}
                              className="flex-1 py-2 px-4 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg font-medium transition-all"
                            >
                              No, I disagree
                            </button>
                          </div>

                          {showAssessmentComment && (
                            <div className="space-y-2 animate-in slide-in-from-top-2">
                              <textarea
                                value={assessmentComment}
                                onChange={(e) => setAssessmentComment(e.target.value)}
                                placeholder="Tell us why you disagree (optional)..."
                                className="w-full p-3 rounded-lg border border-slate-300 focus:border-red-400 focus:outline-none text-sm"
                                rows={3}
                              />
                              <button
                                onClick={() => handleAssessmentFeedback(false)}
                                className="w-full py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-all"
                              >
                                Submit Feedback
                              </button>
                            </div>
                          )}
                        </div>
                      ) : (
                        <p className="text-sm text-emerald-600 font-medium">Thank you for your feedback!</p>
                      )}
                    </div>

                    <button
                      onClick={nextQuestion}
                      className={`mt-4 w-full py-4 rounded-2xl font-bold transition-all ${
                        assessment.is_correct
                        ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-100'
                        : 'bg-slate-900 hover:bg-slate-800 text-white'
                      }`}
                    >
                      {currentQuestionIdx < session.questions.length - 1 ? "Next Question" : "Complete Session"}
                    </button>
                  </div>
                )}

                {hint && !assessment && (
                  <div className="mt-4 p-4 bg-indigo-50 border border-indigo-100 rounded-xl text-indigo-900 flex items-start space-x-3 animate-in slide-in-from-top-2">
                    <Sparkles className="text-indigo-600 mt-1 shrink-0" size={18} />
                    <p className="italic text-sm">{hint}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="py-8 border-t border-slate-100 text-center text-slate-400 text-sm">
        <p>© 2026 Socrates Study Assistant.</p>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) => (
  <div className="p-6 bg-white rounded-2xl border border-slate-100 shadow-sm">
    <div className="mb-4">{icon}</div>
    <h4 className="font-bold text-slate-900 mb-2">{title}</h4>
    <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
  </div>
);

export default App;
