# Waste Classification App

An AI-powered waste classification system that uses computer vision to help users determine which bin (recycling, organics, trash, or special handling) their waste items belong to.

**Status**: Stage 1 Phase 3 Complete - Production-ready Docker deployment with secure environment variable configuration.

## Overview

This application uses OpenAI's vision API to analyze photos of waste items and provide bin recommendations based on material type, form factor, contamination risk, and jurisdiction-specific rules. It features an interactive clarification system for ambiguous items and special handling instructions for hazardous materials.

## Features

### Core Classification System
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

### Architecture (Stage 1 Phase 1 - Complete)
- **Unified Deployment**: Backend serves both API and frontend from a single service
- **Static File Serving**: FastAPI serves web frontend via mounted static files
- **Single Port Access**: Application accessible on one port for simplified deployment
- **Relative API Calls**: Frontend uses same-origin requests, eliminating CORS complexity
- **Cloud-Ready**: Simplified architecture suitable for single-service cloud deployment

## Architecture

The application uses a unified architecture where the FastAPI backend serves both the API and the web frontend.

### Backend (FastAPI)

The backend is built with FastAPI and consists of several key components:

- **`app/main.py`**: API endpoints and static file serving
  - `POST /v1/classify` - Upload image and get bin recommendation
  - `POST /v1/clarify` - Answer clarification questions
  - `GET /health` - Health check endpoint
  - `GET /` - Serves web frontend (index.html)
  - **Static Files**: Mounts `web/` directory for frontend assets (Stage 1 Phase 1)

- **`app/vision_provider.py`**: Computer vision integration
  - OpenAI vision API integration using structured outputs (`responses.parse` with Pydantic models)
  - Stub mode for deterministic testing without API calls
  - Returns `ItemProfile` with normalized attributes: material, form factor, contamination risk, and special handling needs
  - Supports configurable timeout, retries, and base URL override

- **`app/rules.py`**: Decision engine
  - Priority-based decision table operating on `ItemProfile` attributes
  - Scalable design: operates on material classes rather than specific labels
  - Handles special disposal requirements (batteries, e-waste, HHW, sharps)
  - Contamination-aware rules (clean vs. soiled recyclables)
  - Generates clarification questions for ambiguous cases (unknown contamination, uncertain items)
  - Applies user responses to resolve bin assignment

- **`app/schemas.py`**: Pydantic data models
  - `ItemProfile` - Normalized intermediate representation with material, form factor, contamination risk, special handling, and confidence
  - `ClassifyResponse` - Complete API response with result, clarification, and special handling
  - `Result` - Bin assignment with confidence, rationale, and debugging labels
  - `Clarification` - Interactive question structure for ambiguous items
  - `SpecialHandling` - Safety instructions for hazardous items
  - `RationaleItem` - Typed explanation entries (detected item, rule, user input, safety, system)

### Frontend (Web) - Stage 1 Phase 1

Functional vanilla HTML/CSS/JavaScript interface served by the backend:
- **Unified Deployment**: Served by FastAPI backend at root path `/`
- **Same-Origin API**: Uses relative paths to call backend API (no CORS needed)
- Photo upload with camera capture support and image preview
- Real-time classification results with bin badges and confidence display
- Interactive clarification flow (yes/no questions)
- Rationale display showing classification reasoning
- Debug view with formatted JSON responses
- Flexible deployment: configurable API endpoint via URL parameters for testing
- Responsive design with clean, modern UI

## Getting Started

### Prerequisites

**For Docker Deployment (Recommended for Production - Stage 1 Phase 3)**:
- Docker installed on your system
- OpenAI API key (optional, can use stub mode)

**For Local Development**:
- Python 3.9+
- OpenAI API key (optional, can use stub mode)

### Docker Deployment (Stage 1 Phase 3 - Production Ready)

**Quick Start**:

1. Clone the repository:
```bash
git clone <repository-url>
cd waste-classification-app
```

2. Build the Docker image:
```bash
docker build -t waste-classification-app:latest .
```

3. Run the container:

**For stub mode** (testing without API key):
```bash
docker run -p 8000:8000 waste-classification-app:latest
```

**For OpenAI mode** (production with API key):
```bash
docker run -p 8000:8000 \
  -e VISION_PROVIDER=openai \
  -e OPENAI_API_KEY=your-api-key-here \
  -e OPENAI_MODEL=gpt-4o-mini \
  waste-classification-app:latest
```

4. Open your browser to:
```
http://localhost:8000
```

**Environment Variables**:

The application is configured via environment variables (not `.env` files) for production security:

- `VISION_PROVIDER` - Set to `stub` for testing or `openai` for production (default: `stub`)
- `OPENAI_API_KEY` - Your OpenAI API key (required when `VISION_PROVIDER=openai`)
- `OPENAI_MODEL` - OpenAI model to use (default: `gpt-4o-mini`)
- `OPENAI_TIMEOUT_SECONDS` - API timeout in seconds (default: `20`)
- `OPENAI_MAX_RETRIES` - Max retry attempts (default: `2`)
- `OPENAI_BASE_URL` - Optional override for OpenAI API base URL (for proxies)

**Advanced Docker Options**:

```bash
# Run with all environment variables
docker run -p 8000:8000 \
  -e VISION_PROVIDER=openai \
  -e OPENAI_API_KEY=sk-... \
  -e OPENAI_MODEL=gpt-4o-mini \
  -e OPENAI_TIMEOUT_SECONDS=30 \
  -e OPENAI_MAX_RETRIES=3 \
  waste-classification-app:latest

# Run with environment file (create a .env file first)
docker run -p 8000:8000 --env-file .env waste-classification-app:latest

# Run in detached mode with automatic restart
docker run -d --restart unless-stopped \
  -p 8000:8000 \
  -e VISION_PROVIDER=openai \
  -e OPENAI_API_KEY=sk-... \
  --name waste-classifier \
  waste-classification-app:latest
```

### Local Development Installation

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

4. Configure environment variables (Local Development Only):

**For local development**, you can set environment variables in your shell:

```bash
# For stub mode (no API key needed)
export VISION_PROVIDER=stub

# For OpenAI mode
export VISION_PROVIDER=openai
export OPENAI_API_KEY=your-api-key-here
export OPENAI_MODEL=gpt-4o-mini
export OPENAI_TIMEOUT_SECONDS=20
export OPENAI_MAX_RETRIES=2
```

**Note**: Stage 1 Phase 3 removed support for `.env` files for production security. The application now reads environment variables directly from the system. For local development convenience, you can still create a `.env` file and source it manually:

```bash
# Create .env file (not committed to git)
cat > .env << 'EOF'
export VISION_PROVIDER=stub
export OPENAI_API_KEY=your-api-key-here
export OPENAI_MODEL=gpt-4o-mini
EOF

# Source it before running
source .env
```

The application works in stub mode by default if no environment variables are set.

### Running the Application

**Unified Deployment (Stage 1 Phase 1 - Recommended)**

Start the backend which also serves the frontend:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --reload --port 8000
```

Then open your browser to:
```
http://localhost:8000
```

The backend serves:
- Frontend at `/` (root path)
- API endpoints at `/v1/*`
- Health check at `/health`

**Alternative: Separate Frontend Server (Legacy/Development)**

If you need to run frontend separately for development:

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

**Note**: This deployment mode is deprecated for production. Use the unified deployment or Docker instead.

**Remote/Network Access**:

For testing on mobile devices or other machines on your network, replace `localhost` with your server's IP address (e.g., `http://192.168.1.100:8000`). The unified deployment makes this simpler with a single port to expose.

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

## Current Status

### Stage 1 Phase 3 Complete: Docker & Security for Production Readiness
- ✅ Dockerfile for containerized deployment
- ✅ Environment variable configuration (removed `.env` file support for security)
- ✅ CORS middleware removed (unified deployment eliminates cross-origin requests)
- ✅ Non-root user in Docker container for security
- ✅ Removed `python-dotenv` dependency
- ✅ Production-ready deployment with secure API key handling

### Stage 1 Phase 1 Complete: Architecture Unification
- ✅ Backend serves both API and frontend from single service
- ✅ Static file serving via FastAPI `StaticFiles`
- ✅ Root route (`/`) serves web frontend
- ✅ Frontend uses same-origin API calls (no CORS complexity)
- ✅ Single port deployment (cloud-ready)
- ✅ Added `aiofiles` dependency for static file serving

### Core Features Operational
- ✅ FastAPI backend with full error handling and request tracking
- ✅ OpenAI vision API integration with structured outputs (`ItemProfile`)
- ✅ Decision engine with priority-based rules and contamination awareness
- ✅ Multi-bin classification (BLUE/GREEN/GRAY/SPECIAL)
- ✅ Interactive clarification system for ambiguous items
- ✅ Special handling detection and instructions (batteries, e-waste, HHW, sharps)
- ✅ Stub mode for testing without API calls
- ✅ Web frontend with photo upload, results display, and clarification flow

### Current Constraints
- Only supports JPG and PNG images
- Maximum file size: 8MB
- Single jurisdiction (CA_DEFAULT)
- Basic clarification flow (yes/no questions only)
- Simple web UI (no mobile app yet)
- No user authentication or personalization

## Future Enhancements (Stage 1 Phase 2 and Beyond)

### Stage 1 Phase 2 Candidates
- **Enhanced mobile support**: Progressive Web App (PWA) features
- **Improved UI/UX**: Better mobile responsive design, animations, accessibility
- **Performance optimizations**: Caching, image compression, lazy loading
- **Cloud deployment**: Deploy to cloud platform (Azure, AWS, or GCP)

### Future Stages
- **Multi-jurisdiction support**: Customizable rules for different cities/regions with jurisdiction-specific bins and regulations
- **Native mobile applications**: iOS and Android apps with optimized camera integration
- **Enhanced clarification**: Multi-choice questions, image annotations, and contextual help
- **Barcode/packaging scanning**: Direct product lookup for accurate disposal information
- **User feedback loop**: Learn from corrections to improve accuracy over time
- **Batch processing**: Classify multiple items in one photo or process multiple photos
- **Analytics and reporting**: Track waste patterns, diversion rates, and sustainability metrics
- **Integration with local systems**: Direct connection to municipal waste management databases
- **Offline mode**: Local classification for areas with limited connectivity
- **Multilingual support**: Interface and instructions in multiple languages

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
- **Use unified deployment**: Run via Docker or the single uvicorn command (recommended)
- **If using separate servers**: Verify the API base URL with `http://localhost:8080?apiBase=http://localhost:8000`
- **Network access**: For remote access, use server IP instead of localhost

### "Vision provider error" (502)
- **Check VISION_PROVIDER**: Should be "stub" for testing or "openai" for production
- **Verify API key**: If using OpenAI mode, ensure `OPENAI_API_KEY` environment variable is set
- **Check network**: OpenAI API requires internet access
- **Review logs**: Backend console shows detailed error messages
- **Timeout issues**: Increase `OPENAI_TIMEOUT_SECONDS` environment variable if needed

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

This phase established a unified, cloud-ready application architecture:

**Goal Achieved**: Simplified the application into a single deployable unit where the backend serves both API and frontend.

**Key Deliverables**:
1. ✅ **Static File Serving** - FastAPI backend mounts and serves `web/` directory
2. ✅ **Root Route** - `/` endpoint serves frontend `index.html`
3. ✅ **Unified API Access** - Frontend uses same-origin relative paths for API calls
4. ✅ **aiofiles Dependency** - Added required library for `StaticFiles` support
5. ✅ **Single Service Deployment** - Entire application runs on one port
6. ✅ **Simplified CORS** - No cross-origin complexity in unified deployment

**Why This Matters**: Cloud platforms deploy "services." Running the entire application as a single Python service (backend + frontend) is much easier to deploy, manage, and scale than coordinating separate backend and frontend deployments.

**What's Next (Stage 1 Phase 2)**: Focus will likely shift to cloud deployment, mobile optimization, or enhanced user experience features.

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please [open an issue](https://github.com/your-org/waste-classification-app/issues).
