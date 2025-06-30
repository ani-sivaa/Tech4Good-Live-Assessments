import json
import os
from typing import Dict, List

class RubricLoader:
    def __init__(self, rubrics_dir='evaluation/rubrics'):
        self.rubrics_dir = rubrics_dir
        self._ensure_rubrics_dir()
        self._create_default_rubrics()
    
    def _ensure_rubrics_dir(self):
        if not os.path.exists(self.rubrics_dir):
            os.makedirs(self.rubrics_dir)
    
    def _create_default_rubrics(self):
        default_rubrics = {
            'genai_assessment': {
                'name': 'GenAI Assessment Rubric',
                'key_concepts': [
                    'Prompt Design',
                    'Prompt Engineering Techniques',
                    'Evaluation Metrics'
                ],
                'scoring_criteria': {
                    'Prompt Design': {
                        'excellent': 'Demonstrates sophisticated understanding of prompt structure, context, and clarity',
                        'good': 'Shows solid grasp of basic prompt design principles',
                        'needs_improvement': 'Limited understanding of effective prompt construction'
                    },
                    'Prompt Engineering Techniques': {
                        'excellent': 'Applies advanced techniques like few-shot learning, chain-of-thought, etc.',
                        'good': 'Uses some prompt engineering techniques appropriately',
                        'needs_improvement': 'Minimal or incorrect use of prompt engineering techniques'
                    },
                    'Evaluation Metrics': {
                        'excellent': 'Proposes comprehensive and appropriate evaluation metrics',
                        'good': 'Identifies relevant evaluation approaches',
                        'needs_improvement': 'Lacks understanding of proper evaluation methods'
                    }
                },
                'overall_scoring': {
                    'scale': '1-10',
                    'weights': {
                        'Prompt Design': 0.4,
                        'Prompt Engineering Techniques': 0.4,
                        'Evaluation Metrics': 0.2
                    }
                }
            },
            'webdev_assessment': {
                'name': 'Web Development Assessment Rubric',
                'key_concepts': [
                    'Architecture Design',
                    'Code Quality',
                    'User Experience'
                ],
                'scoring_criteria': {
                    'Architecture Design': {
                        'excellent': 'Demonstrates strong architectural thinking and scalability considerations',
                        'good': 'Shows understanding of basic architectural principles',
                        'needs_improvement': 'Limited architectural awareness'
                    },
                    'Code Quality': {
                        'excellent': 'Clean, maintainable, and well-structured code',
                        'good': 'Generally good code practices',
                        'needs_improvement': 'Poor code organization and practices'
                    },
                    'User Experience': {
                        'excellent': 'Strong focus on user-centered design',
                        'good': 'Considers user experience in design decisions',
                        'needs_improvement': 'Minimal attention to user experience'
                    }
                },
                'overall_scoring': {
                    'scale': '1-10',
                    'weights': {
                        'Architecture Design': 0.4,
                        'Code Quality': 0.4,
                        'User Experience': 0.2
                    }
                }
            }
        }
        
        for rubric_name, rubric_data in default_rubrics.items():
            rubric_path = os.path.join(self.rubrics_dir, f'{rubric_name}.json')
            if not os.path.exists(rubric_path):
                with open(rubric_path, 'w') as f:
                    json.dump(rubric_data, f, indent=2)
    
    def load_rubric(self, rubric_name: str) -> Dict:
        rubric_path = os.path.join(self.rubrics_dir, f'{rubric_name}.json')
        
        if not os.path.exists(rubric_path):
            raise FileNotFoundError(f"Rubric '{rubric_name}' not found")
        
        with open(rubric_path, 'r') as f:
            return json.load(f)
    
    def list_rubrics(self) -> List[str]:
        rubrics = []
        for file in os.listdir(self.rubrics_dir):
            if file.endswith('.json'):
                rubrics.append(file.replace('.json', ''))
        return rubrics
    
    def save_rubric(self, rubric_name: str, rubric_data: Dict):
        rubric_path = os.path.join(self.rubrics_dir, f'{rubric_name}.json')
        with open(rubric_path, 'w') as f:
            json.dump(rubric_data, f, indent=2)