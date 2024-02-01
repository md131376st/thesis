from llama_index import Document, Prompt
from llama_index.evaluation import DatasetGenerator


class QuestionGenerator:

    def remove_content_after_section(self ,doc_path, section_title):
        doc = Document(doc_path)
        delete_flag = False

        for paragraph in list(doc.paragraphs):
            if delete_flag:
                p = paragraph._element
                p.getparent().remove(p)
                p._p = p._element = None
            elif section_title in paragraph.text:
                delete_flag = True

    @staticmethod
    def generate_questions(documents, service_context):

        text = "".join([doc.text for doc in documents])
        alldoc = Document(text=text)

        data_generator = DatasetGenerator.from_documents(
            [alldoc],
            text_question_template=Prompt(
                "A sample from the documentations in italian is done below.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Using the documentation sample, carefully follow the instructions below:\n"
                "{query_str}"
            ),
            question_gen_query=(
                "You are an evaluator for a search pipeline. Your task is to write 5 question in italian language\n "
                "using the provided documentation sample above to test the search pipeline. The question should "
                "reference specific names, functions, and terms. Restrict the question to the context information provided. "
                "don't generate questions about indexes of the files they are not port of the evaluatione text. \n"
                "Question: "
            ),
            service_context=service_context
        )
        return data_generator.generate_questions_from_nodes()
