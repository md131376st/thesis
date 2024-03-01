We have two main end points in our system:

1. **Task State**
    - get the state of index store request
   ```
   GET /task/state/<uuid:id>/
   ```

2. **Retrieve**
    - This endpoint is used to retrieve data from the index structure.
    - `question` is a required field. `n_method_results` is also required to specify the number of method results to be
      returned.
    - `n_package_results` and `n_class_results` are optional fields to specify the number of package and class results
      to be returned respectively.
    - `collection_name` is an optional field. If not provided, the search starts from all the repositories.
    - `query_type` is used to set the scope of the search. It supports the following types:
        - all: Searches all the repositories it was indexed in.
        - codebase: Searches in a specific repository.
        - package: Searches in a specific package.
        - class: Searches in a specific class.

   Examples:

    - Couple of repositories
       ```
       POST /index/retrieve
       {
        "question": "your question",
        "n_method_results": 4,
        "n_class_results": 3,
        "n_package_results": 2,
        "query_type": "all"
       }
       ```
    - Whole repository
       ```
       POST /index/retrieve
       {
        "question": "your question",
        "n_method_results": 4,
        "n_class_results": 3,
        "n_package_results": 2,       
        "collection_name":"repo root used for indexing",
        "query_type": "codebase"
       }
       ```
    - Single package
      ```
        POST /index/retrieve
        {
         "question": "your question",
         "n_method_results": 4,
         "n_class_results": 3,
         "collection_name": "your.package.name",
         "query_type": "package"
        }
       ```
    - Single class
      ```
       POST /index/retrieve
       {
        "question": "your question",
        "n_method_results": 4,
        "collection_name": "your.package.name.ClassName",
        "query_type": "class"
       }
       ```

Please note that `n_package_results` and `n_class_results` should not be used with `query_type:class`
and `query_type:package` respectively. If `query_type` is set to `class`, only `n_method_results` should be provided.
Similarly, if `query_type` is set to `package`, only `n_method_results` and `n_class_results` should be provided.

3. **Store**
    - This end point is used to index code bases in a hieratical structure.
    - the end point return the 202 status with a task id that can be used by the Task State to show it's state
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

