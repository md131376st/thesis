from celery import shared_task

from filemanger.models import Document
from filemanger.piplinesteps import TaskHandler
from simplePipline.utils.utilities import log_debug


@shared_task
def process_document(filename):
    log_debug(f"Processing document: {filename}")
    try:
        document = Document.objects.get(file_name=filename)
    except Document.DoesNotExist:
        # Handle the case where the document doesn't exist
        return
    TaskHandler.proccess_data(filename=document.content, is_async=True)
    document.state = Document.State.FilePreporcess
    document.save()
    log_debug(f"Document processing complete: {filename}")


@shared_task
def manage_embedding(collection_name, chunks, metadata, embedding_type, ids):
    log_debug(f"create embedding chunks for collection: {collection_name}")
    TaskHandler.store_embedding(collection_name=collection_name,
                                chunks=chunks,
                                metadata=metadata,
                                embedding_type=embedding_type,
                                ids=ids)
    log_debug(f"end embedding chunks for collection: {collection_name}")
