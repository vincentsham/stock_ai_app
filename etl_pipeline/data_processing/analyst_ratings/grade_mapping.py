from server.database.utils import connect_to_db
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import json

# Load environment variables
load_dotenv()


# Initialize the embedding model
embedding_model_name = os.getenv("OPENAI_EMBEDDING_MODEL")
embedding_model = OpenAIEmbeddings(model=embedding_model_name)


init_grade_mapping = [
    ("Accumulate", "Buy", 1),
    ("Buy", "Buy", 1),
    ("Cautious", "Sell", -1),
    ("Conviction Buy", "Buy", 1),
    ("Equal-Weight", "Hold", 0),
    ("Hold", "Hold", 0),
    ("Market Outperform", "Buy", 1),
    ("Market Perform", "Hold", 0),
    ("Mixed", "Hold", 0),
    ("Negative", "Sell", -1),
    ("Neutral", "Hold", 0),
    ("Outperform", "Buy", 1),
    ("Overweight", "Buy", 1),
    ("Peer Perform", "Hold", 0),
    ("Perform", "Hold", 0),
    ("Positive", "Buy", 1),
    ("Reduce", "Sell", -1),
    ("Sector Perform", "Hold", 0),
    ("Sector Weight", "Hold", 0),
    ("Sell", "Sell", -1),
    ("Strong Buy", "Buy", 1),
    ("Underperform", "Sell", -1),
    ("Underweight", "Sell", -1),
    ("Bullish", "Buy", 1),
    ("Bull", "Buy", 1),
    ("Bearish", "Sell", -1),
    ("Bear", "Sell", -1),
]

ref_grade_list = ["Buy", "Hold", "Sell", "Positive", "Outperform", "Overweight", 
                  "Neutral", "Market Perform", "Equal Weight", 
                  "Negative", "Underperform", "Underweight",  "Reduce", "Cautious",
                  "Bullish", "Bearish"]



def initialize_analyst_grade_mapping_table():
    """
    Initialize the analyst_grade_mapping table with predefined grades and their embeddings.
    Args:
        conn: Database connection object.
    """
    conn = connect_to_db()
    for grade_original, grade_normalized, grade_value in init_grade_mapping:
        embedding = embedding_model.embed_query(grade_original)
        embedding_model_used = embedding_model_name
        insert_record(conn, grade_original, grade_normalized, grade_value, embedding, embedding_model_used)
    conn.commit()
    conn.close()
    return 

def insert_record(conn, grade_original, grade_normalized, grade_value, embedding, embedding_model_used):
    """
    Insert a new record into the analyst_grade_mapping table.
    
    Args:
        conn: Database connection object.
        grade_original (str): The original grade from the analyst.
        grade_normalized (str): The normalized grade (Buy, Hold, Sell).
        grade_value (int): The numerical value associated with the normalized grade.
        embedding (np.ndarray): The embedding vector for the original grade.
        embedding_model_used (str): The name of the embedding model used.
    """
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO ref.analyst_grade_mapping (grade_original, grade_normalized, grade_value, 
                                      embedding, embedding_model, updated_at) VALUES
        (%s, %s, %s, %s, %s, now())
    ON CONFLICT (grade_original, embedding_model) DO NOTHING; 
    """, (grade_original, grade_normalized, grade_value, embedding, embedding_model_used))
    
    return cursor.rowcount


def get_mapping():
    conn = connect_to_db()
    cursor = conn.cursor()
    # Query from the analyst_grade_mapping table
    cursor.execute(f"""
    SELECT grade_original, grade_normalized, grade_value, embedding, embedding_model
    FROM ref.analyst_grade_mapping WHERE embedding_model = '{embedding_model_name}';
    """)
    records = cursor.fetchall()
    # {"Positive": ("BUY", 1, <embedding_vector>, <embedding_model_used>), ...}
    mapping = {}
    for row in records:
        mapping[row[0]] = (row[1], row[2], row[3], row[4])
    conn.close()
    return mapping


def classify_grade_embedding_similarity(new_grade, ref_grade_list, grade_mapping, update=False):
    """
    Classify a new analyst grade into "Buy", "Hold", or "Sell" using embedding similarity.

    """
    new_grade_embedding = embedding_model.embed_query(new_grade)
    # Compute similarity scores
    similarities = {}
    for ref_grade in ref_grade_list:
        ref_embedding = grade_mapping.get(ref_grade, (None, None, None, None))[2]
        if ref_embedding is not None:
            # import pdb; pdb.set_trace()
            ref_embedding = json.loads(ref_embedding)
            similarity = cosine_similarity([np.array(new_grade_embedding)], 
                                           [np.array(ref_embedding)]).mean()
            similarities[ref_grade] = similarity

    new_grade_mapping = grade_mapping[max(similarities, key=similarities.get)]
    # Return the category with the highest similarity
    if update and new_grade not in grade_mapping:
        conn = connect_to_db()
        if insert_record(conn, new_grade, new_grade_mapping[0], new_grade_mapping[1], new_grade_embedding, embedding_model_name) > 0:
            print(f"Inserted new grade mapping for ({new_grade}, {new_grade_mapping[0]}, {new_grade_mapping[1]}) into the database.")
        conn.commit()
        conn.close()

    return (new_grade, new_grade_mapping[0], new_grade_mapping[1])




# Example usage
if __name__ == "__main__":

    initialize_analyst_grade_mapping_table()
    grade_mapping = get_mapping()
    
    # # Example DataFrame value counts for reference
    # test_grade_list = ["Accumulate", "Buy", "Cautious", "Conviction Buy", "Equal-Weight", "Hold", 
    #                    "Market Outperform", "Market Perform", "Mixed", "Negative", "Neutral", 
    #                    "Outperform", "Overweight", "Peer Perform", "Perform", "Positive", "Reduce", 
    #                    "Sector Perform", "Sector Weight", "Sell", "Strong Buy", "Underperform", "Underweight"]
    test_grade_list = ["Excellent"]
    # reference_grades_df = np.array(test_grade_list)
    # # Simulated value counts
  
    for test_grade in test_grade_list:
        classification = classify_grade_embedding_similarity(test_grade, ref_grade_list, grade_mapping, update=True)
        print(f"The grade '{classification[0]}' is classified as: {classification[1]}, {classification[2]}")