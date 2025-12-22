# Waste Classification App

An AI-powered waste classification system that uses computer vision to help users determine which bin (recycling, organics, trash, or special handling) their waste items belong to.

## Overview

This application uses OpenAI's vision API to analyze photos of waste items and provide bin recommendations based on material type, form factor, contamination risk, and jurisdiction-specific rules. It features an interactive clarification system for ambiguous items and special handling instructions for hazardous materials.

## Features

- **Smart Classification**: Analyzes waste items using computer vision and structured decision rules
- **Multi-Bin Support**: Classifies items into:
  - BLUE (Recycling) - Clean recyclable materials
  - GREEN (Organics) - Food waste and compostables
  - GRAY (Landfill/Trash) - Non-recyclable waste
  - SPECIAL - Items requiring special handling (batteries, e-waste, HHW, sharps)
- **Interactive Clarification**: Asks follow-up questions when classification is uncertain
- **Confidence Scoring**: Provides transparency about classification certainty
- **Detailed Rationale**: Explains why items are classified a certain way
- **Jurisdiction Support**: Customizable rules for different locations (currently CA_DEFAULT)

## Architecture

### Backend (FastAPI)

The backend is built with FastAPI and consists of several key components:

- **`app/main.py`**: API endpoints for classification and clarification
  - `POST /v1/classify` - Upload image and get bin recommendation
  - `POST /v1/clarify` - Answer clarification questions
  - `GET /health` - Health check endpoint

- **`app/vision_provider.py`**: Computer vision integration
  - OpenAI vision API integration with structured outputs
  - Stub mode for testing without API calls
  - Returns `ItemProfile` with material, form factor, contamination, and special handling

- **`app/rules.py`**: Decision engine
  - Rules-based classification using decision tables
  - Operates on `ItemProfile` attributes for scalability
  - Handles special cases (batteries, e-waste, food-soiled items)
  - Generates clarification questions for ambiguous cases

- **`app/schemas.py`**: Pydantic data models
  - `ItemProfile` - Structured representation of waste items
  - `ClassifyResponse` - API response format
  - `Result`, `Clarification`, `SpecialHandling` - Supporting schemas

### Frontend (Web)

Simple HTML/JavaScript interface:
- Photo upload with preview
- Real-time classification results
- Interactive clarification questions
- Debug view showing raw JSON responses

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key (optional, can use stub mode)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd waste-classification-app
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

4. Configure environment variables (optional):

Create `backend/app/.env` file:
```env
# Vision provider: "stub" for testing, "openai" for production
VISION_PROVIDER=stub

# OpenAI settings (only needed if VISION_PROVIDER=openai)
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT_SECONDS=20
OPENAI_MAX_RETRIES=2
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --reload --port 8000
```

2. Serve the frontend:
```bash
# In a new terminal
cd web
python -m http.server 8080 --bind 0.0.0.0
```

3. Open your browser and navigate to:
```
http://[SERVER_URL]:8080
```

### Testing

The application works in two modes:

- **Stub mode** (default): Uses deterministic mock data for testing without API calls
- **OpenAI mode**: Uses real vision API for production classification

To test with stub mode, simply upload any image. The stub provider generates deterministic results based on image bytes.

## API Usage

### Classify Image

```bash
curl -X POST http://[SERVER_URL]:8000/v1/classify \
  -F "image=@photo.jpg" \
  -F "jurisdiction_id=CA_DEFAULT"
```

Response:
```json
{
  "request_id": "req_abc123",
  "jurisdiction_id": "CA_DEFAULT",
  "result": {
    "bin": "BLUE",
    "bin_label": "Recycling",
    "confidence": "HIGH",
    "confidence_score": 0.85,
    "rationale": [
      {
        "type": "DETECTED_ITEM",
        "text": "Material: rigid_plastic, Form: bottle, Contamination: low"
      },
      {
        "type": "RULE",
        "text": "Clean recyclable materials go in recycling"
      }
    ],
    "top_labels": []
  },
  "needs_clarification": false,
  "clarification": null,
  "special_handling": null
}
```

### Submit Clarification

```bash
curl -X POST http://[SERVER_URL]:8000/v1/clarify \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_abc123",
    "question_id": "q_food_soiled_01",
    "answer": false
  }'
```

## Technology Stack

- **Backend**: FastAPI, Python 3.9+
- **Vision AI**: OpenAI GPT-4o-mini with structured outputs
- **Image Processing**: Pillow (PIL)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **API Client**: httpx
- **Validation**: Pydantic

## Classification Logic

The system uses a structured approach:

1. **Image Analysis**: Vision AI extracts `ItemProfile` with:
   - Material (paper, plastic, metal, glass, organic, etc.)
   - Form factor (bottle, can, box, bag, etc.)
   - Contamination risk (low, medium, high, unknown)
   - Special handling requirements

2. **Decision Rules**: Applied in priority order:
   - Special handling items (batteries, e-waste, HHW, sharps) → SPECIAL
   - Organic materials → GREEN
   - Clean recyclables → BLUE
   - Film plastic → GRAY (not curbside recyclable)
   - Contaminated items → GRAY or clarification
   - Unknown items → Clarification questions

3. **Confidence Buckets**:
   - HIGH: ≥ 0.85
   - MEDIUM: 0.65-0.84
   - LOW: < 0.65

## Current Limitations (Sprint 0)

- Only supports JPG and PNG images
- Maximum file size: 8MB
- Single jurisdiction (CA_DEFAULT)
- Basic clarification flow
- Simple web UI

## Future Enhancements

- Multi-jurisdiction support with customizable rules
- Mobile app integration
- Barcode/packaging scanning
- User feedback loop for improved accuracy
- Batch processing
- Analytics and reporting
- Integration with local waste management systems

## Development

### Project Structure

```
waste-classification-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # API endpoints
│   │   ├── rules.py             # Classification rules
│   │   ├── schemas.py           # Data models
│   │   └── vision_provider.py  # Vision AI integration
│   └── requirements.txt
├── web/
│   └── index.html              # Frontend interface
├── .gitignore
└── README.md
```

### Adding New Rules

To add classification rules, edit `backend/app/rules.py`:

1. Add new material types to `ItemProfile` schema in `schemas.py`
2. Add decision logic to `decide_bin_from_profile()` function
3. Follow the priority order (special handling → organics → recycling → trash)

### Adding Jurisdictions

To support new jurisdictions:

1. Pass different `jurisdiction_id` in API requests
2. Add jurisdiction-specific logic in `decide_bin_from_profile()`
3. Consider jurisdiction-specific bins, rules, and special handling

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please [open an issue](https://github.com/your-org/waste-classification-app/issues).
