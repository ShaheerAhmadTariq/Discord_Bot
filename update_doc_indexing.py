from embeddings import ChromaHandler

handler = ChromaHandler(path="./chroma_doc")
handler.add_doc_data_to_collection("google")