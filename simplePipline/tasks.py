from celery import shared_task


@shared_task()
def call_embedding(text, embedding, model):
    embedding.apply_embeddings(text, model)
