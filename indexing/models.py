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
