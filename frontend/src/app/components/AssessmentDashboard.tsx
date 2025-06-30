'use client';

import { useState, useEffect } from 'react';

interface Rubric {
  name: string;
  key_concepts: string[];
  scoring_criteria: Record<string, any>;
}

interface EvaluationResult {
  overall_score: number;
  concept_scores: Record<string, any>;
  strengths: string[];
  areas_for_improvement: string[];
  overall_feedback: string;
  rubric_name: string;
  workflow_name: string;
}

export default function AssessmentDashboard() {
  const [rubrics, setRubrics] = useState<string[]>([]);
  const [workflows, setWorkflows] = useState<string[]>([]);
  const [selectedRubric, setSelectedRubric] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState('');
  const [problemStatement, setProblemStatement] = useState('');
  const [studentResponse, setStudentResponse] = useState('');
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const sampleProblemStatement = `Design a GenAI-powered chatbot for customer service. Consider the following:
1. How would you design effective prompts for different customer inquiries?
2. What prompt engineering techniques would you use to ensure consistent responses?
3. How would you evaluate the quality and effectiveness of the chatbot's responses?

Please provide your initial thoughts, approach, and evaluation strategy.`;

  const sampleStudentResponse = `For the GenAI chatbot, I would start by creating a structured prompt template that includes:

1. **Prompt Design**: I'd use a clear instruction format with context about the company, the customer's issue category, and desired tone. For example: "You are a helpful customer service representative for [Company]. The customer has a [billing/technical/general] inquiry. Respond professionally and empathetically."

2. **Prompt Engineering Techniques**: 
   - Few-shot learning: Include 2-3 examples of good customer interactions
   - Chain-of-thought: For complex issues, break down the problem-solving process
   - Role prompting: Clearly define the AI's role and constraints
   - Context injection: Include relevant customer history and product info

3. **Evaluation Metrics**:
   - Response accuracy: Does it address the customer's actual question?
   - Tone appropriateness: Professional yet friendly language
   - Completeness: Are follow-up questions or next steps provided?
   - Hallucination detection: Verify factual claims about products/policies
   - Customer satisfaction scores from post-interaction surveys

I would also implement a feedback loop where poor responses are flagged for prompt refinement.`;

  useEffect(() => {
    fetchRubrics();
    fetchWorkflows();
  }, []);

  const fetchRubrics = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/rubrics');
      const data = await response.json();
      setRubrics(data);
      if (data.length > 0) setSelectedRubric(data[0]);
    } catch (error) {
      console.error('Error fetching rubrics:', error);
      setRubrics(['genai_assessment', 'webdev_assessment']);
      setSelectedRubric('genai_assessment');
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/workflows');
      const data = await response.json();
      setWorkflows(data);
      if (data.length > 0) setSelectedWorkflow(data[0]);
    } catch (error) {
      console.error('Error fetching workflows:', error);
      setWorkflows(['reflection_analysis', 'quick_assessment']);
      setSelectedWorkflow('reflection_analysis');
    }
  };

  const handleEvaluate = async () => {
    if (!problemStatement.trim() || !studentResponse.trim()) {
      alert('Please provide both problem statement and student response');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          problem_statement: problemStatement,
          student_response: studentResponse,
          rubric_name: selectedRubric,
          workflow_name: selectedWorkflow,
        }),
      });

      const result = await response.json();
      if (response.ok) {
        setEvaluationResult(result.evaluation);
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Error evaluating:', error);
      alert('Error connecting to backend. Make sure the Flask server is running.');
    }
    setLoading(false);
  };

  const loadSampleData = () => {
    setProblemStatement(sampleProblemStatement);
    setStudentResponse(sampleStudentResponse);
    setSelectedRubric('genai_assessment');
    setSelectedWorkflow('reflection_analysis');
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Assessment Configuration
          </h2>
          <button
            onClick={loadSampleData}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            Load Sample Data
          </button>
        </div>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Evaluation Rubric
            </label>
            <select
              value={selectedRubric}
              onChange={(e) => setSelectedRubric(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              {rubrics.map(rubric => (
                <option key={rubric} value={rubric}>{rubric}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Evaluation Workflow
            </label>
            <select
              value={selectedWorkflow}
              onChange={(e) => setSelectedWorkflow(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              {workflows.map(workflow => (
                <option key={workflow} value={workflow}>{workflow}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Problem Statement
          </h3>
          <textarea
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="Enter the problem statement for assessment..."
          />
        </div>
        
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Student Response
          </h3>
          <textarea
            value={studentResponse}
            onChange={(e) => setStudentResponse(e.target.value)}
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="Enter the student's reflection or response..."
          />
        </div>
      </div>

      <div className="flex justify-center">
        <button
          onClick={handleEvaluate}
          disabled={loading}
          className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {loading ? 'Evaluating...' : 'Evaluate Response'}
        </button>
      </div>

      {evaluationResult && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Evaluation Results
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <span className="font-medium text-gray-900 dark:text-white">Overall Score</span>
              <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {evaluationResult.overall_score}/10
              </span>
            </div>
            
            {evaluationResult.concept_scores && Object.keys(evaluationResult.concept_scores).length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Concept Scores</h4>
                <div className="space-y-2">
                  {Object.entries(evaluationResult.concept_scores).map(([concept, data]: [string, any]) => (
                    <div key={concept} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                      <span className="text-gray-700 dark:text-gray-300">{concept}</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {data.score || 'N/A'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {evaluationResult.strengths && evaluationResult.strengths.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Strengths</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                  {evaluationResult.strengths.map((strength, index) => (
                    <li key={index}>{strength}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {evaluationResult.areas_for_improvement && evaluationResult.areas_for_improvement.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Areas for Improvement</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                  {evaluationResult.areas_for_improvement.map((area, index) => (
                    <li key={index}>{area}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {evaluationResult.overall_feedback && (
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Overall Feedback</h4>
                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {evaluationResult.overall_feedback}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}