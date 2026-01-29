# TFG Moral Annotation Platform

A comprehensive system for detecting and annotating moral values in news articles using Moral Foundations Theory (MFT). This platform automatically fetches articles from the web, analyzes them for moral foundation values, and stores annotations in both relational (PostgreSQL) and semantic (Apache Jena Fuseki) databases.

**Author**: Ignacio Escribano Benavente  
**Project Type**: TFG (Trabajo de Fin de Grado - Bachelor's Thesis)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
- [Usage](#usage)
  - [Running the API Server](#running-the-api-server)
  - [Running the Fetcher](#running-the-fetcher)
  - [API Endpoints](#api-endpoints)
- [Moral Foundations Theory](#moral-foundations-theory)
- [Data Models](#data-models)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Moral Annotation Platform is designed to analyze news articles through the lens of Moral Foundations Theory, identifying and quantifying moral values expressed in text. The system provides:

- **Automated Article Fetching**: Extract articles from single URLs, batch URLs, or RSS feeds
- **Moral Value Analysis**: Detect and quantify the presence of five moral foundations (Care, Fairness, Loyalty, Authority, Purity)
- **Dual Storage Strategy**: Store data in both relational (PostgreSQL) and semantic (RDF/Fuseki) databases
- **REST API**: Easy integration with external systems through a FastAPI-based interface
- **Semantic Web Support**: RDF triples using the AMOR ontology for advanced semantic queries

## ✨ Features

✅ **Multiple Input Sources**: Support for single URLs, batch URLs, and RSS feeds  
✅ **Intelligent Article Extraction**: Multiple extraction engines (newspaper4k, trafilatura)  
✅ **Moral Foundation Analysis**: Powered by the moralstrength library  
✅ **Dual Database Architecture**: PostgreSQL for relational queries + Fuseki for semantic/ontology queries  
✅ **RESTful API**: FastAPI-based endpoints for all operations  
✅ **Standalone Processing**: Command-line fetcher for batch operations  
✅ **RDF/OWL Support**: AMOR ontology implementation for semantic annotation  
✅ **Docker Ready**: Docker Compose configurations for easy deployment  
✅ **Language Detection**: Automatic detection and handling of article languages  

## 🏗️ Architecture

The platform consists of three main components:

### 1. **Fetcher Component** (`code/fetcher/`)

Responsible for fetching and processing news articles:
- Extracts article content from various sources (URLs, RSS feeds)
- Performs moral value analysis using the moralstrength library
- Handles data insertion into both PostgreSQL and Fuseki databases
- Can be run standalone via command line or integrated via API

### 2. **API Server** (`code/api_server/`)

FastAPI-based REST API providing:
- Endpoints for single, batch, and RSS feed annotation
- End-to-end pipeline orchestration
- Health checks and status monitoring
- Database query interfaces

### 3. **Graph Insert Component** (`code/graph_insert/`)

Utilities for semantic database operations:
- RDF triple generation for AMOR ontology
- SPARQL query management
- Alternative Fuseki handlers

### Data Flow

```
User Request (URL/RSS)
    ↓
API Server (FastAPI)
    ↓
Fetcher: Article Extraction
    ├─ newspaper4k / trafilatura
    ├─ Language Detection
    └─ Text Cleaning
    ↓
Moral Analysis
    ├─ moralstrength library
    ├─ 5 Moral Foundations
    └─ Polarity & Intensity Calculation
    ↓
Dual Database Storage
    ├─ PostgreSQL (Relational)
    │   ├─ newsArticles table
    │   └─ moralAnnotations table
    │
    └─ Fuseki (RDF/Semantic)
        ├─ AMOR Ontology
        └─ SPARQL Triples
    ↓
Response: Annotated Articles
```

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**: Core programming language
- **FastAPI**: Modern web framework for REST API
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM for PostgreSQL
- **Pydantic**: Data validation and serialization

### Data Processing
- **moralstrength**: Moral Foundations Theory analysis
- **newspaper4k**: Web scraping and article extraction
- **trafilatura**: High-performance text extraction
- **feedparser**: RSS feed parsing
- **pandas**: Data manipulation and analysis
- **langdetect**: Language detection

### Databases
- **PostgreSQL 15**: Relational database for structured data
- **Apache Jena Fuseki**: RDF/SPARQL triplestore for semantic data
- **RDFlib**: Python library for RDF manipulation

### Additional Technologies
- **LangChain + OpenAI**: LLM integration for advanced text processing
- **Docker & Docker Compose**: Containerization and orchestration
- **Adminer**: Database management interface

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose** (for databases)
- **Python 3.11** or higher
- **pip** (Python package manager)
- (Optional) **OpenAI API Key** for LangChain features

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Kraslo/TFG_MoralAnnotationPlatform.git
cd TFG_MoralAnnotationPlatform
```

2. **Create and activate a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install the fetcher package**
```bash
cd code/fetcher
pip install -e .
```

4. **Install API server dependencies**
```bash
cd ../api_server
pip install -r requirements.txt
```

### Database Setup

#### 1. Start PostgreSQL

```bash
cd docker/postgre1
docker-compose up -d
```

This starts:
- PostgreSQL server on port `5432`
- Adminer (database UI) on port `8080`

Default credentials:
- Database: `postgres`
- User: `postgres`
- Password: `example`

Access Adminer at: `http://localhost:8080`

#### 2. Start Apache Jena Fuseki

```bash
cd docker/fuseki
docker-compose up -d
```

This starts Fuseki server on port `3030`

Default credentials:
- User: `admin`
- Password: `password`

Access Fuseki UI at: `http://localhost:3030`

#### 3. Create Fuseki Dataset

1. Open Fuseki UI at `http://localhost:3030`
2. Log in with admin credentials
3. Create a new dataset (e.g., `moral_annotations`)
4. Note the dataset name for configuration

### Configuration

Create a `.env` file in the root directory or set environment variables:

```env
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=example

# Fuseki Configuration
FUSEKI_ENDPOINT=http://localhost:3030
FUSEKI_USER=admin
FUSEKI_PASSWORD=password
MORAL_DB=moral_annotations

# Optional: OpenAI for LangChain
OPENAI_API_KEY=your_api_key_here
```

**Note**: The application uses `python-dotenv` to automatically load environment variables from the `.env` file. Alternatively, you can export these variables in your shell or set them in your Docker environment.

## 📖 Usage

### Running the API Server

```bash
cd code/api_server
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

API Documentation (Swagger): `http://localhost:8000/docs`

### Running the Fetcher (Standalone)

The fetcher can be run independently for batch processing:

```bash
cd code/fetcher
python entrypoint.py <URL> [driver]
```

**Arguments:**
- `<URL>`: The URL to fetch (single article, news site, or RSS feed)
- `[driver]`: Optional driver selection:
  - `default`: General web scraping (default)
  - `single`: Single article extraction
  - `rss`: RSS feed parsing

**Examples:**

```bash
# Fetch a single article
python entrypoint.py "https://example.com/article" single

# Process an RSS feed
python entrypoint.py "https://example.com/rss" rss

# Use default driver
python entrypoint.py "https://example.com"
```

### API Endpoints

#### Health Check
```http
GET /moral-annotator/health
```

#### Annotate Single Article
```http
POST /moral-annotator/annotate/single
Content-Type: application/json

{
  "url": "https://example.com/article"
}
```

#### Annotate Batch Articles
```http
POST /moral-annotator/annotate/batch
Content-Type: application/json

{
  "url_list": [
    "https://example.com/article1",
    "https://example.com/article2"
  ]
}
```

#### Annotate RSS Feed
```http
POST /moral-annotator/annotate/rss
Content-Type: application/json

{
  "url": "https://example.com/rss"
}
```

**Note**: This endpoint processes all articles found in the RSS feed. Processing time depends on the number of articles.

#### End-to-End Pipeline (Fetch + Annotate + Store)
```http
POST /moral-annotator/annotate/e2e
Content-Type: application/json

{
  "url": "https://example.com/article"
}
```

#### Retrieve Annotations
```http
GET /moral-annotator/annotations/{article_id}
```

#### Migrate PostgreSQL to Fuseki
```http
POST /moral-annotator/insert/postgre_to_fuseki
```

### Example Response

```json
{
  "article_id": 1,
  "title": "Example Article Title",
  "url": "https://example.com/article",
  "annotations": [
    {
      "moral_foundation": "care",
      "polarity": "virtue",
      "intensity": 7.2,
      "confidence": 0.85,
      "hits": 5
    },
    {
      "moral_foundation": "fairness",
      "polarity": "vice",
      "intensity": 3.8,
      "confidence": 0.72,
      "hits": 3
    }
  ]
}
```

**Note**: `article_id` is auto-generated by the PostgreSQL database (SERIAL type).

## 🧠 Moral Foundations Theory

The platform uses **Moral Foundations Theory (MFT)**, which proposes five innate moral foundations:

| Foundation | Virtue | Vice | Description |
|------------|--------|------|-------------|
| **Care** | Compassion | Harm | Concern for suffering and well-being |
| **Fairness** | Justice | Cheating | Concern for equality and proportionality |
| **Loyalty** | In-group | Betrayal | Commitment to one's group or community |
| **Authority** | Respect | Subversion | Deference to legitimate authority |
| **Purity** | Sanctity | Degradation | Concern for spiritual cleanliness |

### Analysis Process

1. **Text Extraction**: Clean article text is extracted from HTML
2. **Moral Scoring**: The `moralstrength` library analyzes text and assigns scores (0-10) for each foundation
3. **Polarity Assignment**:
   - Score ≥ 5.0: "virtue" (positive expression of the foundation)
   - Score < 5.0: "vice" (negative expression of the foundation)
   - Note: Scores are floating-point values; a score of exactly 5.0 is classified as "virtue"
4. **Metadata**: Includes confidence scores and number of moral terms detected ("hits")

## 📊 Data Models

### PostgreSQL Schema

```sql
-- Articles Table
CREATE TABLE newsArticles (
    id SERIAL PRIMARY KEY,              -- Auto-incrementing unique identifier
    title VARCHAR(500) NOT NULL,
    url TEXT NOT NULL UNIQUE            -- TEXT type to support long URLs
);

-- Annotations Table
CREATE TABLE moralAnnotations (
    id SERIAL PRIMARY KEY,              -- Auto-incrementing unique identifier
    moral_foundation VARCHAR(50) NOT NULL,
    polarity VARCHAR(10) NOT NULL,
    intensity FLOAT NOT NULL,
    confidence FLOAT,
    hits INTEGER,
    article_id INTEGER REFERENCES newsArticles(id)
);
```

### RDF/Fuseki Schema (AMOR Ontology)

```turtle
@prefix : <http://example.org/resource/> .
@prefix amor: <http://example.org/amor#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Annotation Node
:annotation_123 rdf:type amor:MoralValueAnnotation ;
    amor:hasMoralValueCategory amor:Care ;
    amor:hasPolarity amor:virtue ;
    amor:hasPolarityIntensity "7.2"^^xsd:float ;
    amor:hasTarget :article_456 .

# Article Node
:article_456 rdf:type amor:Article ;
    amor:title "Example Article Title" ;
    amor:url "https://example.com/article" .
```

## 📁 Project Structure

```
TFG_MoralAnnotationPlatform/
├── code/
│   ├── api_server/          # FastAPI REST API
│   │   ├── app/
│   │   │   ├── main.py      # Application entry point
│   │   │   ├── routers/     # API endpoints
│   │   │   ├── services/    # Business logic
│   │   │   ├── models/      # Data models
│   │   │   └── api/         # Dependencies & utilities
│   │   ├── tests/           # Test suites
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── fetcher/             # Article fetching & processing
│   │   ├── src/
│   │   │   └── tfg_fetcher/
│   │   │       ├── app/     # Main application logic
│   │   │       ├── handlers/# Database handlers
│   │   │       ├── services/# Core services
│   │   │       ├── models/  # Data models
│   │   │       └── utils/   # Utilities
│   │   ├── entrypoint.py    # CLI entry point
│   │   ├── pyproject.toml
│   │   └── requirements.txt
│   │
│   ├── graph_insert/        # RDF/Fuseki utilities
│   │   └── src/
│   │       ├── handlers/
│   │       └── services/
│   │
│   └── notebooks/           # Jupyter notebooks
│       └── basic_fetching_and_ia.ipynb
│
├── docker/
│   ├── fuseki/              # Apache Jena Fuseki
│   │   └── docker-compose.yaml
│   └── postgre1/            # PostgreSQL + Adminer
│       └── docker-compose.yaml
│
├── .gitignore
└── README.md
```

## ⚙️ Configuration

### Database Connection Strings

**PostgreSQL:**
```python
postgresql://{user}:{password}@{host}:{port}/{database}
# Example: postgresql://postgres:example@localhost:5432/postgres
```

**Fuseki:**
```python
{endpoint}/{dataset}/sparql
# Example: http://localhost:3030/moral_annotations/sparql
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `example` |
| `FUSEKI_ENDPOINT` | Fuseki base URL | `http://localhost:3030` |
| `FUSEKI_USER` | Fuseki admin user | `admin` |
| `FUSEKI_PASSWORD` | Fuseki password | `password` |
| `MORAL_DB` | Fuseki dataset name | `moral_annotations` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |

## 🧪 Testing

The project includes test suites in the `code/api_server/tests` directory.

```bash
cd code/api_server
pytest
```

## 🤝 Contributing

Contributions are welcome! This project is part of a Bachelor's Thesis, but improvements and extensions are appreciated.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests to ensure nothing breaks
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature/my-feature`
7. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where applicable
- Add docstrings to functions and classes
- Keep functions focused and modular

## 📝 License

This project is part of a Bachelor's Thesis (TFG) by Ignacio Escribano Benavente. Please check with the author for licensing information.

## 📚 References

- **Moral Foundations Theory**: Graham, J., Haidt, J., & Nosek, B. A. (2009). Liberals and conservatives rely on different sets of moral foundations. *Journal of Personality and Social Psychology*.
- **moralstrength Library**: [PyPI Package](https://pypi.org/project/moralstrength/)
- **Apache Jena Fuseki**: [Official Documentation](https://jena.apache.org/documentation/fuseki2/)

## 🙏 Acknowledgments

- **moralstrength**: For the moral foundation analysis library
- **newspaper4k**: For article extraction capabilities
- **Apache Jena**: For the Fuseki triplestore
- **FastAPI**: For the excellent web framework

---

**Project Status**: Active Development 🚧

For questions, issues, or contributions, please contact Ignacio Escribano Benavente or open an issue on GitHub.
