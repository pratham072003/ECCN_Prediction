# ECCN Classification Service

An intelligent API service that classifies products into Export Control Classification Numbers (ECCN) using Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs).

## Features

- **Semantic Search**: Utilizes LanceDB and OpenAI `text-embedding-3-small` to retrieve semantically relevant ECCN definitions.
- **LLM Reasoning**: Leverages GPT-4o to analyze product descriptions against retrieved regulatory definitions and notes.
- **Explainability**: Provides a classification decision, confidence score, and detailed reasoning string.
- **Architecture**: Built with Python 3.10 and FastAPI, containerized with Docker for stateless deployment.

## Installation and Setup

### 1. Prerequisites
- Python 3.10 or higher
- Docker (optional, for containerized deployment)
- OpenAI API Key

### 2. Local Environment Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/pratham072003/ECCN_Prediction.git
    cd ECCN_Prediction
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a `.env` file in the root directory:
    ```
    OPENAI_API_KEY=sk-your-key-here
    ```

5.  **Initialize Database:**
    Run the ingestion script to download data and build the LanceDB vector index.
    ```bash
    python run_ingestion.py
    ```

### 3. Running the Service

Start the FastAPI server:
```bash
python main.py
```
The API will be available at `http://127.0.0.1:8000`.

## Docker Deployment

The application is containerized and available on Docker Hub.

### Pull and Run
The container is designed to be stateless. If the vector database is missing at startup, the service will automatically download the dataset and ingest it.

```bash
docker run -p 8000:8000 -e OPENAI_API_KEY="sk-your-key-here" pratham070703/eccn-classifier:latest
```

## API Usage

### Endpoint: `POST /classify`

**Request Body:**
```json
{
  "product_text": "High-performance integrated circuit tailored for radar systems operating at 5GHz with extended temperature range."
}
```

**Response:**
```json
{
  "ecn_number": "3A001",
  "confidence_score": 0.95,
  "reasoning": "The product matches the specific frequency range and power requirements listed in 3A001..."
}
```

## Technical Architecture

The service employs a Hybrid RAG approach:
1.  **Ingestion**: ECCN definitions and notes are embedded into a vector space using OpenAI embeddings and stored in LanceDB.
2.  **Retrieval**: Incoming queries trigger a semantic search to identify the top k most relevant regulatory definitions.
3.  **Reasoning**: A Large Language Model (GPT-4o) evaluates the user query against the retrieved candidates to determine the correct classification.

## Trade-offs and Future Improvements

### Limitations
- **LLM Dependency**: The system relies heavily on the reasoning capabilities of the underlying LLM. Inaccuracies or hallucinations in the model's output directly impact classification quality.
- **Latency**: The two-step process (Vector Retrieval + LLM Generation) introduces higher latency compared to traditional rule-based classifiers, making it less suitable for real-time, high-throughput applications.
- **Static Knowledge Base**: The regulatory data is ingested from a static CSV file. Updates to ECCN regulations require a manual re-run of the ingestion pipeline.

### Future Improvements
- **Fine-tuning**: Fine-tuning a smaller model specifically on export control data could improve accuracy and reduce inference costs.
- **Automated Data Pipeline**: Implementing a connector to fetch the latest ECCN regulations from official sources would ensure the knowledge base remains current.
- **Hybrid Search**: combining dense vector search with sparse keyword search (BM25) would better handle specific regulatory terminology and exact code matches.
