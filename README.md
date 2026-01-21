# ECCN Classification Service

An intelligent API that classifies products into Export Control Classification Numbers (ECCN) using Retrieval-Augmented Generation (RAG) and LLMs.

## 🚀 Features
- **Semantic Search**: Finds the most relevant ECCN codes using vector embeddings (OpenAI `text-embedding-3-small`).
- **LLM Reasoning**: Uses GPT-4o (or similar) to analyze the product description against official definitions and notes.
- **Explainability**: Returns a confidence score and a reasoning string for the classification.

## 🛠️ Setup

1. **Install Dependencies**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   - Open `.env` file.
   - Add your OpenAI Key: `OPENAI_API_KEY=sk-...`

3. **Ingest Data (Build the Brain)**
   This step parses the CSV and builds the ChromaDB vector index.
   ```bash
   python run_ingestion.py
   ```
   *Wait for "Indexing complete."*

## 🏃‍♂️ Running the API

Start the FastAPI server:
```bash
python main.py
```
The API will run at `http://127.0.0.1:8000`.

## 🧪 Usage

**Endpoint**: `POST /classify`

**Request**:
```json
{
  "product_text": "High-performance integrated circuit tailored for radar systems operating at 5GHz with extended temperature range."
}
```

**Response**:
```json
{
  "ecn_number": "3A001",
  "confidence_score": 0.95,
  "reasoning": "The product matches the specific frequency range and power requirements listed in 3A001..."
}
```

## 🐳 Docker Deployment

1. **Build the Image**
   ```bash
   docker build -t eccn-classifier .
   ```
   *(Note: This copies your local `lancedb_data` folder into the image if you have already run the ingestion. If not, you'll need to run ingestion inside the container).*

2. **Run the Container**
   Pass your API Key as an environment variable:
   ```bash
   docker run -p 8000:8000 -e OPENAI_API_KEY="sk-..." eccn-classifier
   ```

3. **Access API**
   Go to `http://localhost:8000/docs`

## 🧠 Technical Approach

1. **Hybrid RAG**: We don't just ask the LLM "What is the ECCN?". We first search our local database for the top 5 official definitions that match the product text.
2. **Context Injection**: We feed those 5 definitions (with their complex regulatory notes) into the LLM context.
3. **Structured Output**: The LLM acts as a judge, selecting the best fit from the candidates and explaining why.
