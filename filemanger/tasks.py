from celery import shared_task, group

from filemanger.models import Document
from filemanger.piplinesteps import TaskHandler
from indexing.ClassCollector import ClassCollector
from simplePipline.utils.utilities import log_debug, Get_json_filename, Get_html_filename


@shared_task()
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


@shared_task()
def manage_embedding(collection_name, batch_list, embedding_type, collection_metadata):
    log_debug(f"create embedding chunks for collection: {collection_name}")
    tasks = []
    for batch in batch_list:
        tasks.append(
            embedding_task.s(
                collection_name,
                batch['chunks'],
                batch['metadata'],
                embedding_type,
                collection_metadata
            ))
    task_group = group(tasks)
    return task_group.apply_async()


@shared_task()
def embedding_task(collection_name, chunks, metadata, embedding_type, collection_metadata):
    TaskHandler.store_embedding(collection_name=collection_name,
                                chunks=chunks,
                                metadata=metadata,
                                embedding_type=embedding_type,
                                collection_metadata=collection_metadata,
                                is_async=True)


@shared_task()
def feature_extract_document(filename, include_images):
    log_debug(f"extract feature: {filename}")
    try:
        document = Document.objects.get(file_name=filename)
    except Document.DoesNotExist:
        # Handle the case where the document doesn't exist
        return
    json_file_name = Get_json_filename(str(document.content))
    html_file_name = Get_html_filename(str(document.content))
    TaskHandler.feature_extraction(input_file=html_file_name,
                                   output_file=json_file_name,
                                   store=True,
                                   include_images=include_images)
    if include_images:
        document.state = Document.State.ImageTextGenerate
    else:
        document.state = Document.State.FeatureExtraction
    document.save()
    log_debug(f"xtract feature complete: {filename}")

    pass


@shared_task()
def class_collector(path, collection_name):
    data_collector = ClassCollector(path, collection_name)
    data_collector.get_class_info()
    return
