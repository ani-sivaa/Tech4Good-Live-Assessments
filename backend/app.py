from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from evaluation.rubric_loader import RubricLoader
from evaluation.workflow_manager import WorkflowManager
from colab_executor import ColabWorkflowManager

load_dotenv()

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

rubric_loader = RubricLoader()
workflow_manager = WorkflowManager()
colab_manager = ColabWorkflowManager()

@app.route('/api/evaluate', methods=['POST'])
def evaluate_student():
    try:
        data = request.json
        
        student_response = data.get('student_response', '')
        problem_statement = data.get('problem_statement', '')
        rubric_name = data.get('rubric_name', 'default')
        workflow_name = data.get('workflow_name', 'default')
        
        # Load rubric and workflow
        rubric = rubric_loader.load_rubric(rubric_name)
        workflow = workflow_manager.load_workflow(workflow_name)
        
        # Generate evaluation prompt
        evaluation_prompt = workflow.generate_prompt(
            student_response=student_response,
            problem_statement=problem_statement,
            rubric=rubric
        )
        
        # Use Gemini to evaluate
        model = genai.GenerativeModel('gemini-flash')
        response = model.generate_content(evaluation_prompt)
        
        # Parse response
        evaluation_result = {
            'raw_response': response.text,
            'rubric_name': rubric_name,
            'workflow_name': workflow_name,
            'evaluation': parse_gemini_response(response.text, rubric)
        }
        
        return jsonify(evaluation_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rubrics', methods=['GET'])
def get_rubrics():
    try:
        rubrics = rubric_loader.list_rubrics()
        return jsonify(rubrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    try:
        workflows = workflow_manager.list_workflows()
        return jsonify(workflows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/colab-workflows', methods=['GET'])
def get_colab_workflows():
    try:
        workflows = colab_manager.list_workflows()
        workflow_info = []
        for workflow in workflows:
            info = colab_manager.get_workflow_info(workflow)
            workflow_info.append(info)
        return jsonify(workflow_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-colab', methods=['POST'])
def execute_colab_workflow():
    try:
        data = request.json
        
        workflow_name = data.get('workflow_name', '')
        student_response = data.get('student_response', '')
        problem_statement = data.get('problem_statement', '')
        rubric_name = data.get('rubric_name', 'genai_assessment')
        
        # Load rubric data
        rubric_data = rubric_loader.load_rubric(rubric_name)
        
        # Prepare parameters for the notebook
        parameters = {
            'student_response': student_response,
            'problem_statement': problem_statement,
            'rubric_data': rubric_data,
            'gemini_api_key': os.getenv('GEMINI_API_KEY')
        }
        
        # Execute the Colab workflow
        result = colab_manager.execute_workflow(workflow_name, parameters)
        
        if result['status'] == 'success':
            # Extract evaluation results from notebook execution
            evaluation_results = extract_colab_results(result['results'])
            
            return jsonify({
                'status': 'success',
                'evaluation': evaluation_results,
                'execution_details': result['results'],
                'workflow_name': workflow_name,
                'rubric_name': rubric_name
            })
        else:
            return jsonify({
                'status': 'error',
                'error': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/live-interview', methods=['POST'])
def start_live_interview():
    try:
        data = request.json
        
        problem_statement = data.get('problem_statement', '')
        key_concepts = data.get('key_concepts', [])
        interview_stage = data.get('stage', 'initial')
        student_input = data.get('student_input', '')
        
        # Generate interview question based on stage
        interview_prompt = generate_interview_prompt(
            problem_statement=problem_statement,
            key_concepts=key_concepts,
            stage=interview_stage,
            student_input=student_input
        )
        
        model = genai.GenerativeModel('gemini-flash')
        response = model.generate_content(interview_prompt)
        
        return jsonify({
            'interviewer_response': response.text,
            'stage': interview_stage,
            'next_stage': get_next_stage(interview_stage)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_gemini_response(response_text, rubric):
    # Simple parsing - in production, this would be more sophisticated
    try:
        # Look for JSON in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
        else:
            # Fallback to structured text parsing
            return {
                'overall_score': 'N/A',
                'feedback': response_text,
                'concept_scores': {}
            }
    except:
        return {
            'overall_score': 'N/A',
            'feedback': response_text,
            'concept_scores': {}
        }

def generate_interview_prompt(problem_statement, key_concepts, stage, student_input):
    if stage == 'initial':
        return f"""
You are conducting a live technical interview for a student. Here is the problem statement:

{problem_statement}

Key concepts to assess: {', '.join(key_concepts)}

The student has just been shown the problem. Ask them to share their initial thoughts and approach. 
Keep your response conversational and encouraging. Don't give away solutions.
"""
    elif stage == 'deep_dive':
        return f"""
You are conducting a live technical interview. The student has shared their initial thoughts:

Student's response: {student_input}

Key concepts to assess: {', '.join(key_concepts)}

Ask a follow-up question to dig deeper into their understanding of one of the key concepts they haven't fully addressed yet.
Be encouraging but probe for deeper technical understanding.
"""
    else:
        return f"""
You are conducting a live technical interview. Continue the conversation based on the student's latest response:

Student's response: {student_input}

Key concepts to assess: {', '.join(key_concepts)}

Ask a thoughtful follow-up question that helps assess their understanding of the remaining concepts.
"""

def extract_colab_results(execution_results):
    """Extract evaluation results from Colab notebook execution"""
    try:
        # Look for the final evaluation results in the last output
        for output_group in reversed(execution_results.get('outputs', [])):
            for output in output_group.get('outputs', []):
                if output.get('type') == 'stream' and 'Final Evaluation Results' in output.get('text', ''):
                    # Try to extract JSON from the output
                    text = output.get('text', '')
                    json_start = text.find('{')
                    if json_start != -1:
                        json_str = text[json_start:]
                        try:
                            return json.loads(json_str)
                        except:
                            pass
        
        # Fallback: construct results from individual outputs
        return {
            'overall_score': 'N/A',
            'feedback': 'Colab workflow executed successfully but results format not recognized',
            'concept_scores': {},
            'workflow_type': 'colab'
        }
    except Exception as e:
        return {
            'overall_score': 'N/A',
            'feedback': f'Error extracting results: {str(e)}',
            'concept_scores': {},
            'workflow_type': 'colab'
        }

def get_next_stage(current_stage):
    stages = ['initial', 'deep_dive', 'clarification', 'wrap_up']
    try:
        current_index = stages.index(current_stage)
        if current_index < len(stages) - 1:
            return stages[current_index + 1]
        else:
            return 'wrap_up'
    except ValueError:
        return 'initial'

if __name__ == '__main__':
    app.run(debug=True, port=5000)