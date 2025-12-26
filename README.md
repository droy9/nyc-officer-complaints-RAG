<p align="center">
  <img src="assets/banner.png" alt="NYC Police Accountability Intelligence" width="100%">
</p>

<h1 align="center">NYC Police Accountability Intelligence</h1>

<p align="center">
  <strong>Natural language access to police misconduct data for impacted communities</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#data-sources">Data Sources</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#usage">Usage</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/LangChain-RAG-green.svg" alt="LangChain">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey.svg" alt="License">
  <img src="https://img.shields.io/badge/status-active%20development-orange.svg" alt="Status">
</p>

---

## Overview

For decades, police misconduct records in New York were hidden from public view under Section 50-a of the Civil Rights Law. When the law was repealed in 2020, it revealed what impacted communities already knew: a pattern of abuse, concentrated on Black and Latino New Yorkers, with limited accountability.

**The data is now public. But it's not accessible.**

Scattered across multiple databases, formatted for analysts rather than advocates, and disconnected from the other systems that shape policing outcomes—the information exists, but the people who need it most can't use it.

This project changes that.

**NYC Police Accountability Intelligence** uses Large Language Models enhanced with Retrieval-Augmented Generation (RAG) to let users ask questions about police misconduct in plain English:

> *"How many complaints has Officer [Name] received for excessive force?"*
>
> *"What's the pattern of stop-and-frisk in my precinct for 14-21 year olds?"*
>
> *"Show me officers with substantiated complaints who are still active."*

---

## Why This Matters

| Statistic | Source |
|-----------|--------|
| **517,000** allegations in CCRB database through 2025 | [50-a.org](https://50-a.org) |
| **99%** of individuals in NYPD Gang Database are Black or Latino | [NAACP LDF](https://www.naacpldf.org/case-issue/nypd-gang-database-policing-tactics/) |
| **5,000+** misconduct complaints filed annually | [NYC CCRB](https://www.nyc.gov/site/ccrb/index.page) |
| **~4,000** officers with substantiated allegations (of 36,000 active) | [ProPublica](https://projects.propublica.org/nypd-ccrb/) |

The gap between data availability and community access is a civil rights issue. This tool is infrastructure for accountability.

---

## Data Sources

### Core Dataset: CCRB Complaints
The Civilian Complaint Review Board database contains records of complaints against NYPD officers since 2000, including:
- Officer identification (name, shield number, rank, command)
- Complaint details (date, location, allegation type)
- Disposition (substantiated, unsubstantiated, unfounded, etc.)
- Penalties imposed (if any)

**Sources:**
- [NYC Open Data - CCRB Tables](https://data.cityofnewyork.us/Public-Safety/Civilian-Complaint-Review-Board-Complaints-Against/2mby-ccnw)
- [NYCLU Misconduct Database](https://www.nyclu.org/data/nypd-misconduct-database)
- [ProPublica NYPD Files](https://projects.propublica.org/nypd-ccrb/)
- [50-a.org Aggregated Records](https://50-a.org)

### Planned Integrations

| Dataset | Description | Status | Priority |
|---------|-------------|--------|----------|
| **Stop, Question & Frisk** | 2003-present SQF encounters with demographic data | 🔜 Planned | High |
| **Gang Database (CGD)** | Criteria analysis, demographic patterns, legal challenges | 🔜 Planned | High |
| **Prosecution Records** | DA charging patterns, case outcomes (web-scraped) | 📋 Research | Medium |
| **PREA Complaints** | Prison Rape Elimination Act complaints in custody | 📋 Research | Medium |
| **Civil Litigation** | Lawsuit settlements, judgments against officers | 📋 Research | Medium |

### Target Demographic Focus
Initial analysis prioritizes **ages 14-21**—the population most impacted by gang database inclusion, stop-and-frisk encounters, and school-to-prison pipeline dynamics.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│              (Natural Language Query Input)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Query Processing                           │
│         (Intent Classification + Entity Extraction)             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Pipeline                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   Embedding   │  │    Vector     │  │   Retrieval   │       │
│  │   Generation  │──│     Store     │──│   + Ranking   │       │
│  │  (OpenAI/HF)  │  │  (Pinecone/   │  │               │       │
│  │               │  │   Chroma)     │  │               │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Response Generation                      │
│         (Context-Aware Answer + Source Citations)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Response Layer                             │
│    (Formatted Answer + Data Visualizations + Source Links)      │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| **LLM** | OpenAI GPT-4 / Claude / Local (Llama) |
| **Embeddings** | OpenAI `text-embedding-3-small` / HuggingFace |
| **Vector Store** | Pinecone / Chroma / Weaviate |
| **Framework** | LangChain / LlamaIndex |
| **Backend** | Python, FastAPI |
| **Frontend** | React / Streamlit (TBD) |
| **Data Processing** | Pandas, DuckDB |

---

## Getting Started

### Prerequisites

```bash
python >= 3.10
pip or poetry
```

### Installation

```bash
# Clone the repository
git clone https://github.com/[org]/nyc-officer-complaints-RAG.git
cd nyc-officer-complaints-RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your API keys to .env
```

### Data Setup

```bash
# Download and process CCRB data
python scripts/download_data.py

# Generate embeddings and populate vector store
python scripts/build_index.py
```

---

## Usage

### Command Line

```bash
python main.py --query "Officers with 5+ excessive force complaints in Brooklyn"
```

### Python API

```python
from accountability_rag import AccountabilityEngine

engine = AccountabilityEngine()

# Simple query
response = engine.query(
    "What percentage of complaints against Officer John Smith were substantiated?"
)
print(response.answer)
print(response.sources)

# Filtered query
response = engine.query(
    "Stop and frisk patterns for 16-year-olds in the 75th precinct",
    filters={"year_range": (2015, 2020), "age_group": "14-21"}
)
```

### Example Queries

| Query | What It Returns |
|-------|-----------------|
| *"List officers with 10+ complaints still on active duty"* | Officer names, complaint counts, current status |
| *"Excessive force trends in the 73rd precinct over time"* | Time series data, visualizations |
| *"Compare CCRB outcomes for Black vs white complainants"* | Substantiation rates by complainant race |
| *"Gang database criteria that led to inclusion of minors"* | Policy analysis, case examples |
| *"Officers involved in both stop-and-frisk and CCRB complaints"* | Cross-database correlation |

---

## Roadmap

### Phase 1: Core RAG System ✅
- [x] CCRB data ingestion pipeline
- [x] Embedding generation + vector store
- [x] Basic natural language query interface
- [x] Source citation in responses

### Phase 2: Data Expansion 🔄
- [ ] Stop, Question & Frisk integration
- [ ] Gang Database analysis layer
- [ ] Age-filtered demographic views (14-21 focus)
- [ ] Precinct-level aggregations

### Phase 3: Advanced Features 📋
- [ ] Prosecution outcome web scraping
- [ ] PREA complaint integration
- [ ] Cross-database officer matching
- [ ] Trend analysis + anomaly detection
- [ ] Public-facing web interface

### Phase 4: Community Tools 📋
- [ ] "Know Your Rights" query mode
- [ ] FOIL request generator
- [ ] Complaint pattern reports for advocacy
- [ ] Embeddable widgets for community organizations

---

## Data Ethics & Privacy

This project handles sensitive data about both officers and complainants. Our principles:

1. **Public data only** — We use only data that is legally public under NY law
2. **No doxxing** — We do not expose personal addresses or non-public information
3. **Context matters** — Allegations are not convictions; we clearly label disposition status
4. **Community-centered** — This tool is built for impacted communities, not surveillance
5. **Transparency** — Our methodology and data sources are fully documented

---

## Related Resources

### Data Sources
- [NYC Open Data - CCRB](https://data.cityofnewyork.us/browse?q=ccrb)
- [NYPD Stop, Question & Frisk Data](https://www.nyc.gov/site/nypd/stats/reports-analysis/stopfrisk.page)
- [50-a.org](https://50-a.org) — Aggregated misconduct records
- [ProPublica NYPD Files](https://projects.propublica.org/nypd-ccrb/)

### Legal Context
- [NAACP LDF: Gang Database Explained](https://www.naacpldf.org/case-issue/nypd-gang-database-policing-tactics/)
- [Legal Aid Society Gang Database Lawsuit (2025)](https://legalaidnyc.org/news/lawsuit-end-nypd-gang-database/)
- [OIG-NYPD Gang Database Report](https://www.nyc.gov/assets/doi/reports/pdf/2023/16CGDRpt.Release04.18.2023.pdf)
- [S.T.O.P. - Guilt by Association Report](https://www.stopspying.org/guilt-by-association)

### Community Organizations
- [Grassroots Advocates for Neighborhood Groups & Solutions (G.A.N.G.S. Coalition)](https://www.naacpldf.org/case-issue/nypd-gang-database-policing-tactics/)
- [NYCLU](https://www.nyclu.org)
- [The Legal Aid Society](https://legalaidnyc.org)
- [The Bronx Defenders](https://www.bronxdefenders.org)

---

## Contributing

We welcome contributions from developers, researchers, legal advocates, and community members.

### Ways to Contribute
- **Data**: Help identify and integrate additional public datasets
- **Code**: Improve RAG pipeline, build visualizations, enhance UI
- **Research**: Document legal context, analyze patterns, write reports
- **Testing**: Use the tool and report issues or suggest improvements
- **Outreach**: Connect us with community organizations who could use this tool

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Lint
ruff check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

This project builds on the work of advocates who fought for decades to repeal 50-a and make police accountability data public. We especially acknowledge:

- **Communities United for Police Reform (CPR)**
- **NAACP Legal Defense Fund**
- **New York Civil Liberties Union**
- **The Legal Aid Society**
- **ProPublica** for their NYPD Files project
- **The G.A.N.G.S. Coalition** and impacted community members

---

<p align="center">
  <strong>Data is power. This tool returns that power to the communities who need it most.</strong>
</p>

<p align="center">
  <a href="https://github.com/[org]/nyc-officer-complaints-RAG/issues">Report Bug</a> •
  <a href="https://github.com/[org]/nyc-officer-complaints-RAG/issues">Request Feature</a> •
  <a href="mailto:contact@example.com">Contact</a>
</p>
