import lancedb
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# LanceDB setup
# Use relative path so it works in Docker (/app/lancedb_data) and Local (./lancedb_data)
LANCE_DB_PATH = "lancedb_data"
TABLE_NAME = "eccn_definitions"

# Initialize OpenAI Client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db():
    return lancedb.connect(LANCE_DB_PATH)

def get_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def get_batch_embeddings(texts):
    # OpenAI suggests replacing newlines for better performance
    texts = [t.replace("\n", " ") for t in texts]
    response = client.embeddings.create(input=texts, model="text-embedding-3-small")
    # Ensure they are in order
    return [d.embedding for d in response.data]

def create_or_get_table(db):
    # Schema is inferred from data usually, but we can just open it if it exists
    if TABLE_NAME in db.table_names():
        return db.open_table(TABLE_NAME)
    return None

def add_documents(db, data):
    """
    data: list of dicts with keys: vector, id, text, ecn_number, parent_ecn, is_leaf
    """
    if TABLE_NAME in db.table_names():
        table = db.open_table(TABLE_NAME)
        table.add(data)
    else:
        # Create table with the first batch
        db.create_table(TABLE_NAME, data)

def query_table(db, query_text, n_results=5):
    if TABLE_NAME not in db.table_names():
        return []
        
    query_vector = get_embedding(query_text)
    table = db.open_table(TABLE_NAME)
    
    results = table.search(query_vector).limit(n_results).to_list()
    return results
