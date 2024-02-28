We have two main end points in our system:

1. **TaskStete**
    - get the state of the index 
    - 
   
2. **Store**
    - This end point is used to store embeddings in chroma db.
    - is_async is used for batching all the chunks and sending to chatgpt embedding api
    - in chunks field each item of the list should be as following
       ```
         {
           "text": "chunk information",
           "id": "scsdv"
         }
         ```
       ```
         {
           "text": "chunk information",
         }
         ```
    - for each chunk in we should have a dictionary in the metadata field.
    - if the length of the metadata doesn't match the metadata will be ignored.
    - in case of empty metadata just put empty list
    - collection_metadata can be an empty dictionary but it must be included. 
    - embedding_type can be any of this values.
        - text-embedding-3-small
        - text-embedding-3-large
        - text-embedding-ada-002

Example:

   ```
   POST /store
   {
    "collection_name": "name of collection",
    "is_async": true,
    "collection_metadata":{},
    "chunks": [
        {
    
            "text": "lite "   
        }

    ],
    "metadata": [{
        "returnType":"ResponseEntity<List<MethodInfoData>>",
        "methodName":"methodName",
        "className":"ParserController",
        "packageName": "com.reply.iriscube.codeparser.controller"
        

    }
    ],
    "embedding_type":"text-embedding-3-small"
   
   }
   ```

2. **Retrieve**
    - This end point is used to retrieve data form the rag system.
    - question and n_results are required fields.
    - embedding_type can be any of this values.
        - text-embedding-3-small
        - text-embedding-3-large
        - text-embedding-ada-002
    - in case not specifying collection_name it will search the root collection MyCodeBase

Example:

   ```
   POST/retrieve 
   {
    "question": "why there is mocks in the tests . what is a unit test?",
    "n_results": 1,
    "embedding_type":"text-embedding-3-small",
    "collection_name": "collection name"
   }
   ```

