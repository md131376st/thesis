We have two main end points in our system:

1. **Task State**
    - get the state of index store request
   ```
   GET /task/state/<uuid:id>/
   ```

2. **Retrieve**
    - This end point is used to retrive data from the index structure
    - question and n_results are required fields.
    - in case collection_name is not provided the search starts form all the repos .
    - query_type is used to set the scope of the search and it supports
        - all ("It searches all the repos it was indexed it")
        - codebase ("Search in a specific repo")
        - package
        - class

   Examples:

    - cuple of repos
       ```
       POST /index/retrieve
       {
        "question": "your question",
        "n_results": 4,
        "query_type": "all"
       }
       ```
        - Whole repo
           ```
           POST /index/retrieve
           {
            "question": "your question",
            "n_results": 4,
            "collection_name":"repo root used for indexing",
            "query_type": "codebase"
         
           }
           ```
        - single package
          ```
            POST /index/retrieve
            {
             "question": "your question",
             "n_results": 4,
             "collection_name": "your.package.name",
             "query_type": "package"
            }
           ```
        - single class
          ```
           POST /index/retrieve
           {
            "question": "your question",
            "n_results": 4,
            "collection_name": "your.package.name.ClassName",
            "query_type": "class"
           }
           ```

3. **Store**
    - This end point is used to index code bases in a hieratical structure.
    - the end point return the 202 status with an task id that can be used by the Task State to show it's state
    - path field is the local path to the repo.
    - indexType field gives the scope of are indexing and can have this values:
        - codebase
        - package
        - class
    - collectionName field has 3 kind of values base on the index type:
        - codebase: is the root package of the code base
        - package: is the package name
        - class: is the qualified_class_name

   Example:

   ```
   POST /index/store
   {
    "path": "/Users/davarimona/Downloads/core-r-metaconto-v1",
    "indexType": "codebase",
    "collectionName": "com.intesasanpaolo.bear.sxdr0.metaconto"
   }
   ```

