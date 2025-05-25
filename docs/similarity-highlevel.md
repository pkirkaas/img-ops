1. Load and normalize all images (OpenCV)
2. Compute embeddings:
    Option A: Use `torchvision.models.resnet50(pretrained=True)`
    Option B: Use `CLIP` if you want semantic understanding
3. Store 512/1024-D feature vectors
4. Use `faiss` to build an index
5. For each image, search top-N similar images
6. Group into clusters based on cosine or Euclidean threshold 




Use sklearn.cluster.DBSCAN or HDBSCAN on vector space to group

Cache embeddings using joblib or persistent storage (e.g., SQLite BLOB or HDF5)