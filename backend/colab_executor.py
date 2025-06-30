import nbformat
import os
import json
import tempfile
from nbconvert import HTMLExporter, PythonExporter
from nbconvert.preprocessors import ExecutePreprocessor
import google.generativeai as genai
from typing import Dict, List, Any, Tuple

class ColabWorkflowExecutor:
    def __init__(self):
        self.execution_timeout = 600  # 10 minutes
        
    def execute_notebook(self, notebook_path: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a Jupyter notebook and return results"""
        try:
            # Read the notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            # Inject parameters if provided
            if parameters:
                nb = self._inject_parameters(nb, parameters)
            
            # Execute the notebook
            ep = ExecutePreprocessor(timeout=self.execution_timeout, kernel_name='python3')
            ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
            
            # Extract results
            results = self._extract_results(nb)
            
            return {
                'status': 'success',
                'results': results,
                'notebook_executed': nb
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'results': {}
            }
    
    def _inject_parameters(self, nb: nbformat.NotebookNode, parameters: Dict[str, Any]) -> nbformat.NotebookNode:
        """Inject parameters into the notebook as the first code cell"""
        param_code = "# Injected parameters\n"
        for key, value in parameters.items():
            if isinstance(value, str):
                param_code += f"{key} = '{value}'\n"
            else:
                param_code += f"{key} = {repr(value)}\n"
        
        # Create parameter cell
        param_cell = nbformat.v4.new_code_cell(source=param_code)
        param_cell.metadata['tags'] = ['parameters']
        
        # Insert at the beginning
        nb.cells.insert(0, param_cell)
        
        return nb
    
    def _extract_results(self, nb: nbformat.NotebookNode) -> Dict[str, Any]:
        """Extract execution results from notebook"""
        results = {
            'outputs': [],
            'variables': {},
            'plots': [],
            'errors': []
        }
        
        for cell_idx, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and hasattr(cell, 'outputs'):
                cell_results = {
                    'cell_index': cell_idx,
                    'source': cell.source,
                    'outputs': []
                }
                
                for output in cell.outputs:
                    if output.output_type == 'execute_result':
                        cell_results['outputs'].append({
                            'type': 'result',
                            'data': output.data
                        })
                    elif output.output_type == 'display_data':
                        cell_results['outputs'].append({
                            'type': 'display',
                            'data': output.data
                        })
                    elif output.output_type == 'stream':
                        cell_results['outputs'].append({
                            'type': 'stream',
                            'name': output.name,
                            'text': output.text
                        })
                    elif output.output_type == 'error':
                        error_info = {
                            'type': 'error',
                            'name': output.ename,
                            'value': output.evalue,
                            'traceback': output.traceback
                        }
                        cell_results['outputs'].append(error_info)
                        results['errors'].append(error_info)
                
                if cell_results['outputs']:
                    results['outputs'].append(cell_results)
        
        return results

class ColabWorkflowManager:
    def __init__(self, workflows_dir='colab_workflows'):
        self.workflows_dir = workflows_dir
        self.executor = ColabWorkflowExecutor()
        self._ensure_workflows_dir()
        self._create_sample_workflows()
    
    def _ensure_workflows_dir(self):
        if not os.path.exists(self.workflows_dir):
            os.makedirs(self.workflows_dir)
    
    def _create_sample_workflows(self):
        """Create sample Colab notebooks for different assessment types"""
        
        # GenAI Assessment Workflow
        genai_notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# GenAI Assessment Workflow\n",
                        "This notebook evaluates student responses for GenAI concepts."
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Parameters (will be injected)\n",
                        "student_response = \"\"\n",
                        "problem_statement = \"\"\n",
                        "rubric_data = {}\n",
                        "gemini_api_key = \"\""
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import google.generativeai as genai\n",
                        "import json\n",
                        "import re\n",
                        "\n",
                        "# Configure Gemini\n",
                        "genai.configure(api_key=gemini_api_key)\n",
                        "model = genai.GenerativeModel('gemini-flash')"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Analyze prompt design quality\n",
                        "def analyze_prompt_design(response):\n",
                        "    prompt = f\"\"\"\n",
                        "    Analyze the following student response for prompt design understanding:\n",
                        "    \n",
                        "    {response}\n",
                        "    \n",
                        "    Rate on a scale of 1-10 and provide specific feedback on:\n",
                        "    1. Understanding of prompt structure\n",
                        "    2. Clarity and specificity\n",
                        "    3. Context awareness\n",
                        "    \n",
                        "    Return as JSON: {{\"score\": X, \"feedback\": \"...\", \"strengths\": [...], \"improvements\": [...]}}\n",
                        "    \"\"\"\n",
                        "    \n",
                        "    response = model.generate_content(prompt)\n",
                        "    try:\n",
                        "        # Extract JSON from response\n",
                        "        json_match = re.search(r'\\{.*\\}', response.text, re.DOTALL)\n",
                        "        if json_match:\n",
                        "            return json.loads(json_match.group())\n",
                        "    except:\n",
                        "        pass\n",
                        "    \n",
                        "    return {\"score\": 5, \"feedback\": response.text, \"strengths\": [], \"improvements\": []}\n",
                        "\n",
                        "prompt_analysis = analyze_prompt_design(student_response)\n",
                        "print(\"Prompt Design Analysis:\")\n",
                        "print(json.dumps(prompt_analysis, indent=2))"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Analyze prompt engineering techniques\n",
                        "def analyze_prompt_engineering(response):\n",
                        "    techniques = [\n",
                        "        \"few-shot learning\", \"chain-of-thought\", \"role prompting\", \n",
                        "        \"context injection\", \"system prompts\", \"temperature control\"\n",
                        "    ]\n",
                        "    \n",
                        "    prompt = f\"\"\"\n",
                        "    Analyze this response for prompt engineering techniques: {', '.join(techniques)}\n",
                        "    \n",
                        "    Student response: {response}\n",
                        "    \n",
                        "    For each technique, indicate if it's mentioned/understood (yes/no) and provide evidence.\n",
                        "    Return as JSON with overall score 1-10.\n",
                        "    \"\"\"\n",
                        "    \n",
                        "    ai_response = model.generate_content(prompt)\n",
                        "    \n",
                        "    # Simple technique detection\n",
                        "    detected_techniques = []\n",
                        "    for technique in techniques:\n",
                        "        if technique.lower() in response.lower():\n",
                        "            detected_techniques.append(technique)\n",
                        "    \n",
                        "    score = min(10, len(detected_techniques) * 2 + 4)\n",
                        "    \n",
                        "    return {\n",
                        "        \"score\": score,\n",
                        "        \"detected_techniques\": detected_techniques,\n",
                        "        \"analysis\": ai_response.text[:500]\n",
                        "    }\n",
                        "\n",
                        "engineering_analysis = analyze_prompt_engineering(student_response)\n",
                        "print(\"\\nPrompt Engineering Analysis:\")\n",
                        "print(json.dumps(engineering_analysis, indent=2))"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Final evaluation\n",
                        "def calculate_final_score(prompt_score, engineering_score, weights):\n",
                        "    total_score = (\n",
                        "        prompt_score * weights.get('Prompt Design', 0.4) +\n",
                        "        engineering_score * weights.get('Prompt Engineering Techniques', 0.4) +\n",
                        "        7 * weights.get('Evaluation Metrics', 0.2)  # Default score for metrics\n",
                        "    )\n",
                        "    return round(total_score, 1)\n",
                        "\n",
                        "weights = rubric_data.get('overall_scoring', {}).get('weights', {\n",
                        "    'Prompt Design': 0.4,\n",
                        "    'Prompt Engineering Techniques': 0.4,\n",
                        "    'Evaluation Metrics': 0.2\n",
                        "})\n",
                        "\n",
                        "final_score = calculate_final_score(\n",
                        "    prompt_analysis['score'],\n",
                        "    engineering_analysis['score'],\n",
                        "    weights\n",
                        ")\n",
                        "\n",
                        "# Compile final results\n",
                        "evaluation_results = {\n",
                        "    \"overall_score\": final_score,\n",
                        "    \"concept_scores\": {\n",
                        "        \"Prompt Design\": prompt_analysis,\n",
                        "        \"Prompt Engineering Techniques\": engineering_analysis\n",
                        "    },\n",
                        "    \"workflow_type\": \"colab_genai_assessment\"\n",
                        "}\n",
                        "\n",
                        "print(f\"\\nFinal Evaluation Results:\")\n",
                        "print(json.dumps(evaluation_results, indent=2))"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Save sample notebook
        genai_path = os.path.join(self.workflows_dir, 'genai_assessment.ipynb')
        if not os.path.exists(genai_path):
            with open(genai_path, 'w') as f:
                json.dump(genai_notebook, f, indent=2)
    
    def list_workflows(self) -> List[str]:
        """List available Colab workflow notebooks"""
        workflows = []
        for file in os.listdir(self.workflows_dir):
            if file.endswith('.ipynb'):
                workflows.append(file.replace('.ipynb', ''))
        return workflows
    
    def execute_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific Colab workflow"""
        notebook_path = os.path.join(self.workflows_dir, f'{workflow_name}.ipynb')
        
        if not os.path.exists(notebook_path):
            return {
                'status': 'error',
                'error': f'Workflow {workflow_name} not found'
            }
        
        return self.executor.execute_notebook(notebook_path, parameters)
    
    def get_workflow_info(self, workflow_name: str) -> Dict[str, Any]:
        """Get information about a workflow"""
        notebook_path = os.path.join(self.workflows_dir, f'{workflow_name}.ipynb')
        
        if not os.path.exists(notebook_path):
            return {'error': 'Workflow not found'}
        
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            # Extract metadata and description
            description = "No description available"
            if nb.cells and nb.cells[0].cell_type == 'markdown':
                description = nb.cells[0].source
            
            return {
                'name': workflow_name,
                'description': description,
                'cell_count': len(nb.cells),
                'language': nb.metadata.get('kernelspec', {}).get('language', 'python')
            }
        except Exception as e:
            return {'error': str(e)}