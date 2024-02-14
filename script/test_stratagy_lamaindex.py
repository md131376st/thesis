import chromadb

chroma_client = chromadb.PersistentClient("db")
lamIndex_chroma_db= chromadb.EphemeralClient()
if __name__ == '__main__':
    pass