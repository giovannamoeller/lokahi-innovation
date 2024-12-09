# FindCare AI - Healthcare Analytics Platform

FindCare AI is a comprehensive healthcare analytics platform that transforms complex healthcare data into actionable insights. Using advanced AI and data processing, it helps healthcare professionals understand and improve community health outcomes across different regions.

## Features

- **Regional Analysis**: Deep dive into specific area health metrics
- **Comparative Analysis**: Cross-regional health patterns analysis
- **AI-Driven Insights**: Automated analysis and recommendations using Groq LLM
- **Interactive Visualizations**: Easy-to-understand data representation
- **Real-time Processing**: Analysis of 6.6M+ healthcare records across 48 MSA regions

## Tech Stack

### Backend
- FastAPI
- pandas
- langchain_groq
- Python data processing libraries

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Recharts for data visualization
- Lucide React for icons

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Groq API key
- Healthcare data files (parquet format)

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Create `.env` file:
```env
GROQ_API_KEY=your-groq-api-key
SERVICES_PATH=./data/Claims_Services
MEMBERS_PATH=./data/Claims_Member
ENROLLMENT_PATH=./data/Claims_Enrollment
PROVIDERS_PATH=./data/Claims_Provider
```

4. Run the server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

## API Endpoints

- `GET /api/msas` - Get list of available MSAs
- `POST /api/analyze` - Generate analysis for specific MSA
- `POST /api/compare` - Compare multiple MSAs
- `GET /api/stats` - Get overall statistics
- `GET /api/health` - Health check endpoint

## Data Processing

The platform processes healthcare data including:
- Member demographics
- Healthcare services
- Enrollment information
- Provider data

## Acknowledgments

- Built for the Lōkahi Healthcare Accelerator Hackathon
- Uses Groq's language models for AI analysis
- Healthcare data provided by the hackathon organizers

## Contact

Giovanna Moeller - contact@giovannamoeller.com
