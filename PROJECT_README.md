# Tech4Good Live Assessment Tool

An AI-powered assessment platform for conducting scalable live interviews and evaluating student responses using GenAI technology.

## Features

- **Offline Assessment**: Evaluate student reflection documents against customizable rubrics
- **Live Interview**: Conduct real-time AI-powered interviews with students
- **Flexible Rubrics**: Easily swap between different evaluation criteria and workflows
- **GenAI Integration**: Uses Google's Gemini Flash model for intelligent evaluation

## Project Structure

```
├── frontend/          # Next.js React application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── AssessmentDashboard.tsx
│   │   │   │   └── LiveInterview.tsx
│   │   │   └── page.tsx
├── backend/           # Flask Python API
│   ├── app.py         # Main Flask application
│   ├── evaluation/    # Evaluation system
│   │   ├── rubric_loader.py      # Rubric management
│   │   ├── workflow_manager.py   # Workflow management
│   │   ├── rubrics/              # JSON rubric definitions
│   │   └── workflows/            # JSON workflow definitions
│   └── .env.example   # Environment variables template
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install flask flask-cors python-dotenv google-generativeai
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

5. Run the Flask server:
```bash
python app.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### Assessment Dashboard
- Upload problem statements and student responses
- Select evaluation rubrics and workflows
- Get detailed AI-powered assessments with scores and feedback

### Live Interview
- Set up interview problems and key concepts to assess
- Conduct real-time conversations with AI interviewer
- AI asks follow-up questions to probe deeper understanding

## Customization

### Adding New Rubrics

Create a new JSON file in `backend/evaluation/rubrics/`:

```json
{
  "name": "Custom Assessment Rubric",
  "key_concepts": ["Concept 1", "Concept 2"],
  "scoring_criteria": {
    "Concept 1": {
      "excellent": "Description for excellent performance",
      "good": "Description for good performance", 
      "needs_improvement": "Description for needs improvement"
    }
  },
  "overall_scoring": {
    "scale": "1-10",
    "weights": {
      "Concept 1": 0.6,
      "Concept 2": 0.4
    }
  }
}
```

### Adding New Workflows

Create a new JSON file in `backend/evaluation/workflows/`:

```json
{
  "name": "Custom Workflow",
  "description": "Description of the workflow",
  "prompt_template": "Your custom prompt template with {variables}",
  "evaluation_type": "offline"
}
```

## API Endpoints

- `POST /api/evaluate` - Evaluate student responses
- `GET /api/rubrics` - List available rubrics
- `GET /api/workflows` - List available workflows  
- `POST /api/live-interview` - Conduct live interview sessions

## Requirements

- Python 3.8+
- Node.js 16+
- Google Gemini API key

## Key Concepts Evaluated

- **Prompt Design**: Understanding of effective prompt structure and clarity
- **Prompt Engineering Techniques**: Application of advanced prompting methods
- **Evaluation Metrics**: Knowledge of appropriate assessment approaches