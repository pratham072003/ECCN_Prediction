import pandas as pd
import os
from .rag_engine import get_db, add_documents, get_batch_embeddings

# Use relative path for Docker compatibility
DATA_PATH = "data/eccn_data.csv"

def load_data_and_index():
    print("Loading data...")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    
    # Basic cleaning
    df['notes'] = df['notes'].fillna('')
    df['description_en'] = df['description_en'].fillna('')
    
    # Create a combined text for embedding
    df['embedding_text'] = df.apply(
        lambda row: f"ECCN: {row['ecn_number']}\nDescription: {row['description_en']}\nNotes: {row['notes']}", 
        axis=1
    )
    
    print("Generating embeddings and indexing into LanceDB...")
    db = get_db()
    
    # Process in batches to respect API limits and memory
    batch_size = 50 # OpenAI batch limit is often higher, but 50 is safe
    total = len(df)
    
    all_data = []
    
    for i in range(0, total, batch_size):
        batch_df = df.iloc[i : i + batch_size]
        texts = batch_df['embedding_text'].tolist()
        
        try:
            embeddings = get_batch_embeddings(texts)
            
            for idx, row in enumerate(batch_df.itertuples()):
                # Explicitly cast everything to string to avoid PyArrow type errors with NaNs (floats)
                record = {
                    "vector": embeddings[idx],
                    "id": str(row.derived_ecn_no),
                    "text": str(row.embedding_text),
                    "ecn_number": str(row.ecn_number) if pd.notna(row.ecn_number) else "",
                    "parent_ecn": str(row.parent_ecn) if pd.notna(row.parent_ecn) else "",
                    "is_leaf": str(row.is_leaf)
                }
                all_data.append(record)
                
            print(f"Processed {min(i + batch_size, total)}/{total}")
            
        except Exception as e:
            print(f"Error processing batch {i}: {e}")
            
    if all_data:
        add_documents(db, all_data)
        print("Indexing complete.")
    else:
        print("No data was indexed.")

if __name__ == "__main__":
    load_data_and_index()
