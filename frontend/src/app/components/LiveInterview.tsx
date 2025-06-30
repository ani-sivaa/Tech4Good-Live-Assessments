'use client';

import { useState } from 'react';

interface InterviewMessage {
  type: 'interviewer' | 'student';
  content: string;
  timestamp: Date;
}

interface InterviewResponse {
  interviewer_response: string;
  stage: string;
  next_stage: string;
}

export default function LiveInterview() {
  const [messages, setMessages] = useState<InterviewMessage[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [problemStatement, setProblemStatement] = useState('');
  const [keyConcepts, setKeyConcepts] = useState<string[]>([]);
  const [currentStage, setCurrentStage] = useState('initial');
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [loading, setLoading] = useState(false);

  const sampleProblem = `Design a GenAI-powered system for automated code review. Consider the following aspects:

1. **Prompt Design**: How would you structure prompts to analyze code for different types of issues (bugs, style, security, performance)?

2. **Prompt Engineering Techniques**: What techniques would you use to ensure the AI provides consistent, actionable feedback?

3. **Evaluation Metrics**: How would you measure the effectiveness of the AI code reviewer?

Take your time to think through this problem and share your initial approach.`;

  const sampleConcepts = ['Prompt Design', 'Prompt Engineering Techniques', 'Evaluation Metrics'];

  const startInterview = async () => {
    if (!problemStatement.trim() || keyConcepts.length === 0) {
      alert('Please provide a problem statement and key concepts');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/live-interview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          problem_statement: problemStatement,
          key_concepts: keyConcepts,
          stage: 'initial',
          student_input: '',
        }),
      });

      const result: InterviewResponse = await response.json();
      
      if (response.ok) {
        const initialMessage: InterviewMessage = {
          type: 'interviewer',
          content: result.interviewer_response,
          timestamp: new Date(),
        };
        setMessages([initialMessage]);
        setCurrentStage(result.next_stage);
        setInterviewStarted(true);
      } else {
        alert(`Error: ${result}`);
      }
    } catch (error) {
      console.error('Error starting interview:', error);
      
      const fallbackMessage: InterviewMessage = {
        type: 'interviewer',
        content: `Hello! I see you have a problem about ${problemStatement.slice(0, 50)}... 

Let's start by having you share your initial thoughts. What's your first impression of this problem, and how would you approach solving it?

Take your time to think through the key concepts we need to cover: ${keyConcepts.join(', ')}.`,
        timestamp: new Date(),
      };
      setMessages([fallbackMessage]);
      setCurrentStage('deep_dive');
      setInterviewStarted(true);
    }
    setLoading(false);
  };

  const sendMessage = async () => {
    if (!currentInput.trim()) return;

    const studentMessage: InterviewMessage = {
      type: 'student',
      content: currentInput,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, studentMessage]);
    setCurrentInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/live-interview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          problem_statement: problemStatement,
          key_concepts: keyConcepts,
          stage: currentStage,
          student_input: currentInput,
        }),
      });

      const result: InterviewResponse = await response.json();
      
      if (response.ok) {
        const interviewerMessage: InterviewMessage = {
          type: 'interviewer',
          content: result.interviewer_response,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, interviewerMessage]);
        setCurrentStage(result.next_stage);
      } else {
        const errorMessage: InterviewMessage = {
          type: 'interviewer',
          content: 'I apologize, but I encountered an issue. Could you please repeat your response?',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: InterviewMessage = {
        type: 'interviewer',
        content: 'Great point! Can you elaborate more on that aspect? I\'d like to understand your thinking process better.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    setLoading(false);
  };

  const resetInterview = () => {
    setMessages([]);
    setCurrentInput('');
    setCurrentStage('initial');
    setInterviewStarted(false);
  };

  const loadSampleData = () => {
    setProblemStatement(sampleProblem);
    setKeyConcepts(sampleConcepts);
  };

  const addConcept = () => {
    const concept = prompt('Enter a key concept:');
    if (concept && concept.trim()) {
      setKeyConcepts(prev => [...prev, concept.trim()]);
    }
  };

  const removeConcept = (index: number) => {
    setKeyConcepts(prev => prev.filter((_, i) => i !== index));
  };

  if (!interviewStarted) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Interview Setup
            </h2>
            <button
              onClick={loadSampleData}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              Load Sample Problem
            </button>
          </div>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Problem Statement
              </label>
              <textarea
                value={problemStatement}
                onChange={(e) => setProblemStatement(e.target.value)}
                rows={10}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Enter the problem statement for the live interview..."
              />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Key Concepts to Assess
                </label>
                <button
                  onClick={addConcept}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                >
                  Add Concept
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {keyConcepts.map((concept, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full dark:bg-blue-900 dark:text-blue-300"
                  >
                    {concept}
                    <button
                      onClick={() => removeConcept(index)}
                      className="ml-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={startInterview}
                disabled={loading || !problemStatement.trim() || keyConcepts.length === 0}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? 'Starting Interview...' : 'Start Interview'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg flex flex-col h-[600px]">
        <div className="flex justify-between items-center p-4 border-b dark:border-gray-700">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Live Interview Session
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Stage: {currentStage} | Concepts: {keyConcepts.join(', ')}
            </p>
          </div>
          <button
            onClick={resetInterview}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            End Interview
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.type === 'student' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] p-3 rounded-lg ${
                  message.type === 'student'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                }`}
              >
                <div className="text-sm font-medium mb-1">
                  {message.type === 'student' ? 'You' : 'Interviewer'}
                </div>
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div className="text-xs opacity-75 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg">
                <div className="text-sm font-medium mb-1">Interviewer</div>
                <div className="text-gray-600 dark:text-gray-400">Thinking...</div>
              </div>
            </div>
          )}
        </div>
        
        <div className="p-4 border-t dark:border-gray-700">
          <div className="flex space-x-2">
            <input
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Type your response..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !currentInput.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
}