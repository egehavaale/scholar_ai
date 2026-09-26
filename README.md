# SmartDoc Summarizer & Entity Extractor

SmartDoc Summarizer & Entity Extractor is a desktop application designed for document ingestion, natural language summarization, structured entity extraction, and local archival storage. The system is engineered using PySide6 (Qt) for the user interface, Hugging Face Transformers for text synthesis, statistical and regular expression pipelines for entity identification, and SQLAlchemy 2.0 with SQLite for persistent local storage.

---

## Technical Architecture

```
+-------------------------------------------------------------------------+
|                        PySide6 Desktop Interface                        |
|                                                                         |
|  +---------------------------+  +------------------------------------+  |
|  |     Archive Sidebar       |  |       Workspace & Controls         |  |
|  |  - Document History       |  |  - Document Ingestion (.pdf/.docx) |  |
|  |  - Search & Retrieval     |  |  - Raw Text Editor                 |  |
|  |  - Record Deletion        |  |  - Progress Bar (QThread-backed)   |  |
|  +-------------+-------------+  +-----------------+------------------+  |
+----------------|----------------------------------|---------------------+
                 |                                  |
                 v                                  v
+--------------------------------+  +-------------------------------------+
|        Database Layer          |  |         NLP & Analytics Engine      |
|                                |  |                                     |
|  - SQLAlchemy 2.0 (ORM)        |  |  1. Ingestion & Preprocessing       |
|  - SQLite (smartdoc.db)        |  |     - File Decoder (.pdf, .docx)    |
|  - Table: documents            |  |     - Whitespace & Character Normal |
|    * id (PK)                   |  |     - Overlapping Chunk Generator   |
|    * filename                  |  |                                     |
|    * raw_text                  |  |  2. Summarization Pipeline          |
|    * summary                   |  |     - DistilBART-CNN-12-6 (Local)   |
|    * keywords_json             |  |     - Extractive Fallback Engine    |
|    * created_at                |  |                                     |
|    * status                    |  |  3. Extraction Pipeline             |
|                                |  |     - Regex Entity Parser           |
|                                |  |       (Emails, URLs, Dates, DOIs)   |
|                                |  |     - Frequency & N-gram Extractor  |
+--------------------------------+  +-------------------------------------+
```

---

## Key Modules

### 1. NLP & Analytics Engine (`nlp_engine.py`)
- **Document Ingestion**: Supports `.txt`, `.pdf` (via `pypdf`), and `.docx` (via `python-docx`) with multi-encoding fallback.
- **Preprocessing & Chunking**: Cleans control characters, normalizes line breaks, and divides extensive documents into overlapping windows (default: 500-600 words with 50-word overlap) to respect transformer context boundaries.
- **Summarization**: Utilizes the Hugging Face `transformers` summarization pipeline loaded on CPU/GPU (`sshleifer/distilbart-cnn-12-6`). If dependencies or model weights are missing, the engine automatically degrades to a deterministic frequency-based extractive summarizer.
- **Entity & Keyword Extraction**:
  - Regex extraction for academic citations (`[1]`, `(Author, Year)`), acronyms, organizations, emails, URLs/DOIs, and numeric metrics.
  - Statistical unigram and bigram extraction filtered against multi-language stopword dictionaries.

### 2. Database Layer (`database.py`)
- Built on **SQLAlchemy 2.0** declarative syntax (`Mapped`, `mapped_column`).
- Local **SQLite** backend with connection pooling and thread-safe session handling.
- Encapsulates schema definitions, document retrieval, search ordering, and deletion operations.

### 3. Graphical User Interface (`app.py`)
- Engineered with **PySide6** and a dark corporate design system (`QSS`).
- Decoupled asynchronous analysis using `QThread` and worker signals (`AnalysisWorker`) to prevent UI blocking during heavy inference tasks.
- Live progress reporting through `QProgressBar`.
- Tabbed reporting interface:
  - Executive Summary view with clipboard integration.
  - Structured Entity & Keyword table with column filtering.
  - Raw JSON metrics viewer for integration with other tooling.

---

## Dependencies

The core runtime dependencies are defined in `requirements.txt`:

| Package | Version | Purpose |
|---|---|---|
| `PySide6` | >= 6.5.0 | Desktop GUI framework |
| `SQLAlchemy` | >= 2.0.0 | Relational database ORM |
| `transformers` | >= 4.35.0 | Pre-trained summarization models |
| `torch` | >= 2.0.0 | Neural network execution backend |
| `pypdf` | >= 3.17.0 | PDF document parser |
| `python-docx` | >= 1.0.0 | Microsoft Word (.docx) parser |

---

## Installation & Setup

### 1. Prerequisites
- Python 3.9 through Python 3.13.
- Recommended: Python virtual environment (`venv`).

### 2. Virtual Environment Configuration

#### Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Execution

Launch the desktop interface from the project root:

```bash
python app.py
```

The application creates and initializes the local SQLite database (`smartdoc.db`) automatically upon initial launch.

---

## Model Configuration & Offline Operation

### Default Model
The system initializes with `sshleifer/distilbart-cnn-12-6`. When first executed with internet connectivity, the model weights (~1.2 GB) are cached locally in the user's Hugging Face cache directory:
- Linux/macOS: `~/.cache/huggingface/hub/`
- Windows: `C:\Users\<Username>\.cache\huggingface\hub\`

### Offline & Lightweight Mode
If `torch` or `transformers` is unavailable, or if the environment lacks an active network connection for initial weight downloading, the engine switches to the built-in Extractive Summarizer without throwing runtime exceptions.

To use an alternative model, pass the model identifier to `NLPEngine` in `nlp_engine.py`:
```python
nlp_engine = NLPEngine(model_name="facebook/bart-large-cnn")
```

---

## Database Management

The local database file `smartdoc.db` contains the `documents` table:

```sql
CREATE TABLE documents (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    raw_text TEXT NOT NULL,
    summary TEXT,
    keywords_json TEXT,
    created_at DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL
);
```

Database queries can be executed directly using any standard SQLite CLI or client.
