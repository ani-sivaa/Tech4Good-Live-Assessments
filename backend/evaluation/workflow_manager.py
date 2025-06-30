import json
import os
from typing import Dict, List

class WorkflowManager:
    def __init__(self, workflows_dir='evaluation/workflows'):
        self.workflows_dir = workflows_dir
        self._ensure_workflows_dir()
        self._create_default_workflows()
    
    def _ensure_workflows_dir(self):
        if not os.path.exists(self.workflows_dir):
            os.makedirs(self.workflows_dir)
    
    def _create_default_workflows(self):
        default_workflows = {
            'reflection_analysis': {
                'name': 'Reflection Document Analysis',
                'description': 'Analyzes student reflection documents for key concepts',
                'prompt_template': """
You are an expert evaluator for technical assessments. Please analyze the following student reflection document.

**Problem Statement:**
{problem_statement}

**Student Reflection:**
{student_response}

**Evaluation Rubric:**
{rubric_text}

Please evaluate the student's response based on the rubric criteria. For each key concept, provide:
1. A score based on the rubric scale
2. Specific feedback explaining the score
3. Areas for improvement

Format your response as JSON with the following structure:
{{
    "overall_score": <number>,
    "concept_scores": {{
        "concept_name": {{
            "score": <number>,
            "feedback": "detailed feedback",
            "evidence": "specific quotes from student response"
        }}
    }},
    "strengths": ["list of strengths"],
    "areas_for_improvement": ["list of areas to work on"],
    "overall_feedback": "comprehensive feedback summary"
}}
""",
                'evaluation_type': 'offline'
            },
            'live_interview': {
                'name': 'Live Interview Assessment',
                'description': 'Conducts real-time interviews with students',
                'prompt_template': """
You are conducting a live technical assessment interview. Your goal is to evaluate the student's understanding of key concepts through conversation.

**Problem Statement:**
{problem_statement}

**Key Concepts to Assess:**
{key_concepts}

**Current Stage:** {interview_stage}

**Student's Latest Response:**
{student_response}

**Instructions:**
- Ask thoughtful follow-up questions
- Probe for deeper understanding
- Be encouraging but thorough
- Don't give away answers
- Guide the conversation to cover all key concepts

Respond with your next interview question or comment.
""",
                'evaluation_type': 'live'
            },
            'quick_assessment': {
                'name': 'Quick Concept Check',
                'description': 'Fast evaluation for basic concept understanding',
                'prompt_template': """
Quickly evaluate this student response for understanding of key concepts.

**Problem:** {problem_statement}
**Student Response:** {student_response}
**Key Concepts:** {key_concepts}

Provide a brief assessment (1-2 sentences per concept) and an overall score out of 10.

Response format:
- Overall Score: X/10
- Quick Feedback: [brief summary]
- Concept Understanding: [list each concept with brief note]
""",
                'evaluation_type': 'quick'
            }
        }
        
        for workflow_name, workflow_data in default_workflows.items():
            workflow_path = os.path.join(self.workflows_dir, f'{workflow_name}.json')
            if not os.path.exists(workflow_path):
                with open(workflow_path, 'w') as f:
                    json.dump(workflow_data, f, indent=2)
    
    def load_workflow(self, workflow_name: str) -> 'Workflow':
        workflow_path = os.path.join(self.workflows_dir, f'{workflow_name}.json')
        
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Workflow '{workflow_name}' not found")
        
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)
        
        return Workflow(workflow_data)
    
    def list_workflows(self) -> List[str]:
        workflows = []
        for file in os.listdir(self.workflows_dir):
            if file.endswith('.json'):
                workflows.append(file.replace('.json', ''))
        return workflows

class Workflow:
    def __init__(self, workflow_data: Dict):
        self.name = workflow_data['name']
        self.description = workflow_data['description']
        self.prompt_template = workflow_data['prompt_template']
        self.evaluation_type = workflow_data.get('evaluation_type', 'offline')
    
    def generate_prompt(self, **kwargs) -> str:
        # Format rubric for inclusion in prompt
        if 'rubric' in kwargs:
            rubric = kwargs['rubric']
            rubric_text = self._format_rubric(rubric)
            kwargs['rubric_text'] = rubric_text
            
            # Extract key concepts from rubric
            if 'key_concepts' not in kwargs:
                kwargs['key_concepts'] = ', '.join(rubric.get('key_concepts', []))
        
        try:
            return self.prompt_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for workflow: {e}")
    
    def _format_rubric(self, rubric: Dict) -> str:
        rubric_text = f"Rubric: {rubric.get('name', 'Assessment Rubric')}\n\n"
        
        if 'key_concepts' in rubric:
            rubric_text += "Key Concepts to Evaluate:\n"
            for concept in rubric['key_concepts']:
                rubric_text += f"- {concept}\n"
            rubric_text += "\n"
        
        if 'scoring_criteria' in rubric:
            rubric_text += "Scoring Criteria:\n"
            for concept, criteria in rubric['scoring_criteria'].items():
                rubric_text += f"\n{concept}:\n"
                for level, description in criteria.items():
                    rubric_text += f"  {level.title()}: {description}\n"
        
        if 'overall_scoring' in rubric:
            scoring = rubric['overall_scoring']
            rubric_text += f"\nOverall Scoring Scale: {scoring.get('scale', '1-10')}\n"
            
            if 'weights' in scoring:
                rubric_text += "Concept Weights:\n"
                for concept, weight in scoring['weights'].items():
                    rubric_text += f"  {concept}: {weight * 100}%\n"
        
        return rubric_text