import pickle
import gzip

# Load the original similarity.pkl
with open("similarity.pkl", "rb") as f_in:
    similarity_data = pickle.load(f_in)

# Compress and save as similarity.pkl.gz
with gzip.open("similarity.pkl.gz", "wb") as f_out:
    pickle.dump(similarity_data, f_out)

print("✅ similarity.pkl compressed to similarity.pkl.gz")



