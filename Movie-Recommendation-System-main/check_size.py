import os

size = os.path.getsize("similarity.pkl.gz") / (1024 * 1024)
print(f"📦 Compressed size: {size:.2f} MB")
