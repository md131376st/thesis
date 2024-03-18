from mongoengine import Document, fields


class MethodRecord(Document):
    method_name = fields.StringField()
    qualified_class_name = fields.StringField()
    package_name = fields.StringField()
    codebase_name = fields.StringField()
    chromadb_collection_name = fields.StringField()
    collection_metadata = fields.DictField()

    description = fields.StringField()
    metadata = fields.DictField()
    technical_questions = fields.ListField()
    functional_questions = fields.ListField()
    meta = {
        'indexes': [
            ('codebase_name', 'qualified_class_name')
        ]
    }

    def __str__(self):
        return self.method_name

    def to_dict(self):
        return {
            "chunks": [
                {
                    "text": self.description,
                    "id": str(self.id)
                }
            ],
            "metadata": [
                self.metadata
            ],
            "collection_metadata": self.collection_metadata,
            "collection_name": self.qualified_class_name,
            "name": self.method_name
        }


class ClassRecord(Document):
    qualified_class_name = fields.StringField()
    package_name = fields.StringField()
    codebase_name = fields.StringField()
    chromadb_collection_name = fields.StringField()

    description = fields.StringField()
    metadata = fields.DictField()
    technical_questions = fields.ListField()
    functional_questions = fields.ListField()
    meta = {
        'indexes': [
            ('codebase_name', 'package_name'),
            'qualified_class_name'
        ]
    }


class PackageRecord(Document):
    package_name = fields.StringField()
    codebase_name = fields.StringField()
    chromadb_collection_name = fields.StringField()

    description = fields.StringField()
    metadata = fields.DictField()
    technical_questions = fields.ListField()
    functional_questions = fields.ListField()
    meta = {
        'indexes': [
            'codebase_name',
            'package_name'
        ]
    }
