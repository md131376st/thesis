from indexing.storageManger.BasicSotrageManger import BasicStorageManger


class CodeBaseStorageManger(BasicStorageManger):
    def __init__(self, collection_name, codebase_name):

        super().__init__(collection_name, codebase_name)
