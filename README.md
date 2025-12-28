# Waste Classification App

An AI-powered waste classification system that uses computer vision to help users determine which bin (recycling, organics, trash, or special handling) their waste items belong to.

**Status**: Stage 1 Phase 1 Complete - Core classification system operational with vision AI integration, multi-bin support, and interactive clarification.

## Overview

This application uses OpenAI's vision API to analyze photos of waste items and provide bin recommendations based on material type, form factor, contamination risk, and jurisdiction-specific rules. It features an interactive clarification system for ambiguous items and special handling instructions for hazardous materials.

## Features

### Core Classification (Stage 1 Phase 1 - Complete)
- **Smart Classification**: Analyzes waste items using OpenAI vision API with structured outputs (`ItemProfile`)
- **Multi-Bin Support**: Classifies items into:
  - BLUE (Recycling) - Clean recyclable materials (paper, cardboard, metal, glass, rigid plastic)
  - GREEN (Organics) - Food waste and compostables
  - GRAY (Landfill/Trash) - Non-recyclable waste and contaminated items
  - SPECIAL - Items requiring special handling (batteries, e-waste, HHW, sharps)
- **Interactive Clarification**: Asks follow-up questions for ambiguous cases (e.g., food-soiled paper)
- **Confidence Scoring**: Provides transparency with HIGH/MEDIUM/LOW confidence levels and numeric scores
- **Detailed Rationale**: Explains classification decisions with structured rationale items
- **Flexible Testing**: Stub mode for development/testing without API calls, OpenAI mode for production
- **Error Handling**: Comprehensive error handling with request tracking and user-friendly error messages

## Architecture

### Backend (FastAPI)

The backend is built with FastAPI and consists of several key components:

- **`app/main.py`**: API endpoints for classification and clarification
  - `POST /v1/classify` - Upload image and get bin recommendation
  - `POST /v1/clarify` - Answer clarification questions
  - `GET /health` - Health check endpoint

- **`app/vision_provider.py`**: Computer vision integration (Stage 1 Phase 1)
  - OpenAI vision API integration using structured outputs (`responses.parse` with Pydantic models)
  - Stub mode for deterministic testing without API calls
  - Returns `ItemProfile` with normalized attributes: material, form factor, contamination risk, and special handling needs
  - Supports configurable timeout, retries, and base URL override

- **`app/rules.py`**: Decision engine (Stage 1 Phase 1)
  - Priority-based decision table operating on `ItemProfile` attributes
  - Scalable design: operates on material classes rather than specific labels
  - Handles special disposal requirements (batteries, e-waste, HHW, sharps)
  - Contamination-aware rules (clean vs. soiled recyclables)
  - Generates clarification questions for ambiguous cases (unknown contamination, uncertain items)
  - Applies user responses to resolve bin assignment

- **`app/schemas.py`**: Pydantic data models (Stage 1 Phase 1)
  - `ItemProfile` - Normalized intermediate representation with material, form factor, contamination risk, special handling, and confidence
  - `ClassifyResponse` - Complete API response with result, clarification, and special handling
  - `Result` - Bin assignment with confidence, rationale, and debugging labels
  - `Clarification` - Interactive question structure for ambiguous items
  - `SpecialHandling` - Safety instructions for hazardous items
  - `RationaleItem` - Typed explanation entries (detected item, rule, user input, safety, system)

### Frontend (Web) - Stage 1 Phase 1

Functional vanilla HTML/CSS/JavaScript interface:
- Photo upload with camera capture support and image preview
- Real-time classification results with bin badges and confidence display
- Interactive clarification flow (yes/no questions)
- Rationale display showing classification reasoning
- Debug view with formatted JSON responses
- Configurable API endpoint via URL parameters for flexible deployment
- Responsive design with clean, modern UI

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

4. Configure environment variables:

Create `backend/app/.env` file (optional - required for OpenAI mode):
```env
# Vision provider: "stub" for testing, "openai" for production
VISION_PROVIDER=stub

# OpenAI settings (only needed if VISION_PROVIDER=openai)
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT_SECONDS=20
OPENAI_MAX_RETRIES=2

# Optional: Override OpenAI base URL (for proxies or custom endpoints)
# OPENAI_BASE_URL=https://api.openai.com/v1
```

**Note**: The application works without a `.env` file using stub mode by default.

### Running the Application

**Option 1: Unified Deployment (Recommended)**

Start the backend which also serves the frontend:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --reload --port 8000
```

Then open your browser to:
```
http://localhost:8000
```

The backend serves the frontend at the root path and provides API endpoints at `/v1/*`.

**Option 2: Separate Frontend Server (Development)**

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --reload --port 8000
```

2. In a new terminal, serve the frontend:
```bash
cd web
python -m http.server 8080 --bind 0.0.0.0
```

3. Open your browser and navigate to:
```
http://localhost:8080
```

**Remote/Network Access**:

For testing on mobile devices or other machines on your network, replace `localhost` with your server's IP address (e.g., `http://192.168.1.100:8000`). You can also override the API endpoint via URL parameter:
```
http://192.168.1.100:8080?apiBase=http://192.168.1.100:8000
```

### Testing

The application supports two operating modes:

**Stub Mode** (default - for development/testing):
- Uses deterministic mock data without external API calls
- No OpenAI API key required
- Generates realistic `ItemProfile` objects based on image bytes
- Useful for testing classification logic, UI flows, and error handling
- To use: Set `VISION_PROVIDER=stub` in `.env` or omit the variable

**OpenAI Mode** (production):
- Uses real OpenAI vision API with structured outputs
- Requires valid `OPENAI_API_KEY`
- Returns actual vision analysis from GPT-4o-mini or configured model
- To use: Set `VISION_PROVIDER=openai` and configure API key in `.env`

Simply upload any image to test the classification flow. In stub mode, different images (based on content hash) will produce different mock classifications to simulate variety.

## API Endpoints

### `POST /v1/classify`
Upload an image for waste classification.

**Request**:
- `image` (file, required): JPG or PNG image, max 8MB
- `jurisdiction_id` (form field, optional): Default "CA_DEFAULT"
- `client_request_id` (form field, optional): Client-provided request ID for tracking
- `locale` (form field, optional): Future use for internationalization

**Response**: `ClassifyResponse` with bin assignment, confidence, rationale, and optional clarification/special handling

**Status Codes**:
- `200 OK`: Successful classification
- `400 Bad Request`: Invalid image format
- `413 Payload Too Large`: Image exceeds 8MB
- `415 Unsupported Media Type`: Not JPG or PNG
- `502 Bad Gateway`: Vision provider error

### `POST /v1/clarify`
Answer a clarification question from a previous classification.

**Request Body** (JSON):
```json
{
  "request_id": "req_abc123def456",
  "question_id": "q_food_soiled_01",
  "answer": true,
  "top_labels": [{"label": "paper box", "score": 0.75}]
}
```

**Response**: `ClassifyResponse` with updated bin assignment based on answer

### `GET /health`
Health check endpoint.

**Response**: `{"status": "ok"}`

### `GET /`
Serves the web frontend (index.html)

### `GET /favicon.ico`
Returns 204 No Content (prevents 404 errors in logs)

## API Usage Examples

### Classify Image

```bash
curl -X POST http://localhost:8000/v1/classify \
  -F "image=@photo.jpg" \
  -F "jurisdiction_id=CA_DEFAULT"
```

Response:
```json
{
  "request_id": "req_abc123def456",
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
    "top_labels": [
      {"label": "plastic bottle", "score": 0.85}
    ]
  },
  "needs_clarification": false,
  "clarification": null,
  "special_handling": null
}
```

### Submit Clarification

When `needs_clarification` is `true`, answer the question:

```bash
curl -X POST http://localhost:8000/v1/clarify \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_abc123def456",
    "question_id": "q_food_soiled_01",
    "answer": false,
    "top_labels": [{"label": "paper box", "score": 0.75}]
  }'
```

Response returns updated `ClassifyResponse` with final bin assignment.

## Technology Stack

**Backend**:
- **FastAPI** 0.115.6 - Modern, fast web framework with automatic API documentation
- **Python** 3.9+ - Core language
- **Pydantic** - Data validation and structured outputs
- **Pillow (PIL)** 12.0.0 - Image processing and normalization

**AI/ML**:
- **OpenAI API** 2.11.0 - Vision analysis with GPT-4o-mini
- **Structured Outputs** - Pydantic-based response parsing via `responses.parse`

**HTTP & Async**:
- **httpx** 0.27.2 - Async HTTP client with timeout configuration
- **uvicorn** 0.32.1 - ASGI server with standard extras

**Frontend**:
- **Vanilla JavaScript** - No framework dependencies
- **HTML5/CSS3** - Modern, responsive design
- **Fetch API** - HTTP requests to backend

**Development**:
- **python-dotenv** 1.0.1 - Environment configuration
- **python-multipart** 0.0.12 - File upload handling
- **aiofiles** 24.1.0 - Async file operations

## Classification Logic

The system uses a structured, scalable approach completed in Stage 1 Phase 1:

1. **Image Analysis**: Vision AI (OpenAI with structured outputs) extracts `ItemProfile`:
   - **Material**: paper_cardboard, rigid_plastic, film_plastic, metal, glass, organic, textile, unknown
   - **Form factor**: bottle, can, box, bag_film, cup, tray, utensil, sheet, mixed, unknown
   - **Contamination risk**: low (clean/dry), medium (some residue), high (heavily soiled), unknown
   - **Special handling**: battery, e_waste, hhw (household hazardous waste), sharps, none
   - **Confidence**: 0.0 to 1.0 numeric score
   - **Raw labels**: Debugging information with top detected labels

2. **Decision Rules**: Applied in priority order via decision tables:
   - **Priority 1**: Special handling items (batteries, e-waste, HHW, sharps) → SPECIAL with safety instructions
   - **Priority 2**: Organic materials → GREEN
   - **Priority 3**: Clean recyclables (paper, metal, glass, rigid plastic with low contamination) → BLUE
   - **Priority 4**: Film plastic → GRAY (not curbside recyclable)
   - **Priority 5**: Contaminated recyclables → GRAY or clarification based on contamination level
   - **Priority 6**: Unknown material/form factor → Clarification questions
   - **Fallback**: Conservative approach requests clarification for uncertain items

3. **Confidence Buckets**:
   - **HIGH**: ≥ 0.85 - Strong classification certainty
   - **MEDIUM**: 0.65-0.84 - Moderate certainty, may include clarification
   - **LOW**: < 0.65 - Low certainty, typically triggers clarification

4. **Clarification Flow**:
   - System asks yes/no questions when uncertain (e.g., "Is it food-soiled?")
   - User responses applied via `apply_clarification()` to determine final bin
   - Maintains request context and previous labels for continuity

## Current Status (Stage 1 Phase 1 - Complete)

### What's Working
- ✅ FastAPI backend with full error handling and request tracking
- ✅ OpenAI vision API integration with structured outputs (`ItemProfile`)
- ✅ Decision engine with priority-based rules and contamination awareness
- ✅ Multi-bin classification (BLUE/GREEN/GRAY/SPECIAL)
- ✅ Interactive clarification system for ambiguous items
- ✅ Special handling detection and instructions (batteries, e-waste, HHW, sharps)
- ✅ Stub mode for testing without API calls
- ✅ Web frontend with photo upload, results display, and clarification flow
- ✅ Static file serving from unified backend
- ✅ CORS configuration for development

### Current Constraints
- Only supports JPG and PNG images
- Maximum file size: 8MB
- Single jurisdiction (CA_DEFAULT)
- Basic clarification flow (yes/no questions only)
- Simple web UI (no mobile app yet)
- No user authentication or personalization

## Future Enhancements (Stage 1 Phase 2 and Beyond)

- **Multi-jurisdiction support**: Customizable rules for different cities/regions with jurisdiction-specific bins and regulations
- **Mobile applications**: Native iOS and Android apps with optimized camera integration
- **Enhanced clarification**: Multi-choice questions, image annotations, and contextual help
- **Barcode/packaging scanning**: Direct product lookup for accurate disposal information
- **User feedback loop**: Learn from corrections to improve accuracy over time
- **Batch processing**: Classify multiple items in one photo or process multiple photos
- **Analytics and reporting**: Track waste patterns, diversion rates, and sustainability metrics
- **Integration with local systems**: Direct connection to municipal waste management databases
- **Offline mode**: Local classification for areas with limited connectivity
- **Multilingual support**: Interface and instructions in multiple languages
- **Accessibility improvements**: Voice commands, screen reader support, and simplified interfaces

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

To extend classification rules, edit `backend/app/rules.py`:

1. **Add new material types** to `ItemProfile` in `backend/app/schemas.py`:
   ```python
   material: Literal["paper_cardboard", "rigid_plastic", ..., "new_material"]
   ```

2. **Add decision logic** to `decide_bin_from_profile()` function in `backend/app/rules.py`

3. **Follow the priority order**:
   - Special handling (batteries, e-waste, HHW, sharps) - highest priority
   - Organics
   - Clean recyclables  
   - Film plastics and non-recyclables
   - Contaminated items
   - Unknown items (trigger clarification)

4. **Update vision prompts** in `backend/app/vision_provider.py` if new materials need different detection instructions

**Example**: Adding textile recycling:
```python
# In schemas.py
material: Literal[..., "textile"]

# In rules.py, after organics but before general recyclables:
if profile.material == "textile" and profile.contamination_risk == "low":
    return Result(bin="SPECIAL", bin_label="Textile Recycling", ...)
```

### Adding Jurisdictions

To support new jurisdictions with different rules:

1. **Pass jurisdiction_id** in API requests:
   ```bash
   curl -X POST http://localhost:8000/v1/classify \
     -F "image=@photo.jpg" \
     -F "jurisdiction_id=NYC_MANHATTAN"
   ```

2. **Add jurisdiction-specific logic** in `decide_bin_from_profile()`:
   ```python
   def decide_bin_from_profile(profile: ItemProfile, jurisdiction_id: str = "CA_DEFAULT"):
       if jurisdiction_id == "NYC_MANHATTAN":
           # NYC-specific rules (e.g., film plastic accepted at drop-off)
           if profile.material == "film_plastic":
               return special_recycling_result()
       # Default CA rules...
   ```

3. **Consider jurisdiction differences**:
   - Accepted materials (e.g., glass in single-stream vs. separate)
   - Bin colors and labels (different naming conventions)
   - Special handling locations (local drop-off sites)
   - Contamination thresholds (stricter vs. lenient)
   - Organics program availability

**Future enhancement**: Externalize rules to JSON/YAML configuration files for easier management.

## Troubleshooting

### Frontend can't connect to backend
- **Check API endpoint**: If running separate servers, verify the API base URL
- **Use URL parameter override**: `http://localhost:8080?apiBase=http://localhost:8000`
- **Check CORS**: Backend allows `localhost:8080` and `localhost:8000` by default
- **Network access**: For remote access, use server IP instead of localhost

### "Vision provider error" (502)
- **Check VISION_PROVIDER**: Should be "stub" for testing or "openai" for production
- **Verify API key**: If using OpenAI mode, ensure `OPENAI_API_KEY` is set in `.env`
- **Check network**: OpenAI API requires internet access
- **Review logs**: Backend console shows detailed error messages
- **Timeout issues**: Increase `OPENAI_TIMEOUT_SECONDS` if needed

### "File too large" error (413)
- Maximum file size is 8MB
- Compress or resize images before upload
- Use JPG format for smaller file sizes

### "Unsupported media type" error (415)
- Only JPG and PNG images are supported in Stage 1 Phase 1
- Convert other formats (HEIC, WebP, etc.) to JPG or PNG

### Classification seems inaccurate
- **Stub mode**: Using deterministic mock data, not real AI - set `VISION_PROVIDER=openai` for production
- **Photo quality**: Take clear, well-lit photos with one item centered
- **Contamination**: Ensure you answer clarification questions accurately
- **Model limitations**: Vision AI may struggle with unusual items or poor lighting

### Server won't start
- **Check Python version**: Requires Python 3.9+
- **Install dependencies**: Run `pip install -r backend/requirements.txt`
- **Port conflict**: Change port if 8000 is in use: `uvicorn app.main:app --port 8001`
- **Module not found**: Ensure you're running from `backend/` directory

### Web frontend shows blank page
- **Check console**: Browser console shows JavaScript errors
- **Verify backend**: Ensure backend is running and accessible
- **Static files**: Verify `web/index.html` exists relative to backend
- **File serving**: Backend mounts static files from `web/` directory

## Stage 1 Phase 1 Completion Summary

This phase established the core foundation of the waste classification system:

**Key Deliverables**:
1. ✅ **Vision AI Integration** - OpenAI structured outputs returning normalized `ItemProfile`
2. ✅ **Classification Engine** - Priority-based decision tables with contamination awareness
3. ✅ **Multi-bin Support** - BLUE, GREEN, GRAY, and SPECIAL bin classifications
4. ✅ **Clarification System** - Interactive yes/no questions for ambiguous items
5. ✅ **Special Handling** - Safety instructions for batteries, e-waste, HHW, and sharps
6. ✅ **Web Interface** - Functional photo upload and results display
7. ✅ **Developer Experience** - Stub mode, error handling, request tracking, and CORS support

**What's Next (Stage 1 Phase 2)**:
- Enhanced clarification with multi-choice questions
- Improved UI/UX with better mobile support
- Performance optimizations and caching
- Extended testing and accuracy improvements
- Additional material types and jurisdiction support

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please [open an issue](https://github.com/your-org/waste-classification-app/issues).
