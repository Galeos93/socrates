
import { GoogleGenAI } from "@google/genai";

// Fix: Initializing GoogleGenAI using process.env.API_KEY directly per guidelines
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export const geminiService = {
  /**
   * Provides a Socratic hint without giving away the answer.
   */
  async getSocraticHint(questionText: string, context?: string): Promise<string> {
    try {
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: `I am a student studying the following question: "${questionText}". 
        The context is: "${context || 'General knowledge'}".
        Provide me with a brief Socratic hint that guides me toward the answer without telling me directly. 
        Be encouraging and brief.`,
        config: {
          thinkingConfig: { thinkingBudget: 0 }
        }
      });
      return response.text || "Try thinking about the core concepts mentioned in the text.";
    } catch (error) {
      console.error("Gemini hint error:", error);
      return "Reflect on how this concept relates to the document's main point.";
    }
  },

  /**
   * Explains a complex concept from the document in simpler terms.
   */
  async explainConcept(concept: string): Promise<string> {
    try {
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: `Explain the following study concept simply as if I am 12 years old: "${concept}"`,
        config: {
          thinkingConfig: { thinkingBudget: 0 }
        }
      });
      return response.text || "This concept is a building block for what we are learning.";
    } catch (error) {
      console.error("Gemini explanation error:", error);
      return "Consult the source document for more details on this topic.";
    }
  }
};