import os

from llama_index import ServiceContext
from llama_index.llms import OpenAI

from simplePipline.Loader.documentLoader import DocumentLoader
from simplePipline.test.questionGenrator import QuestionGenerator


class TestPipline:
    def __init__(self, version, filepath):
        self.filepath = filepath
        self.version = version
        self.question_dataset = self.get_test_set()
        self.gpt4_service_context = ServiceContext.from_defaults(llm=OpenAI(llm="gpt-4", temperature=0))
        self.responses = []

    def run(self):
        pass

    def generate_questions(self):
        documents = DocumentLoader().load_data(self.filepath)
        generated_questions = QuestionGenerator.generate_questions(documents, self.gpt4_service_context)

        with open("../question_dataset.txt", "w") as file:
            for question in generated_questions:
                file.write(f"{question.strip()}\n")
        return generated_questions

    def get_test_set(self):
        if os.path.exists("../question_dataset.txt"):
            return self.read_questions_from_file("../question_dataset.txt")
        else:
            return self.generate_questions()

    def read_questions_from_file(self, filepath):
        with open(filepath, "r") as file:
            return [line.strip() for line in file]

    def test_hallucination(self):
        pass

    def test_correction(self):
        pass
