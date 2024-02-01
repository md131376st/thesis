from llama_index import Response

from llama_index.llms import OpenAI

from llama_index import ServiceContext
from llama_index.evaluation import FaithfulnessEvaluator, QueryResponseEvaluator

import os
import asyncio

from simplePipline.Loader.documentLoader import DocumentLoader
from simplePipline.testing.questionGenrator import QuestionGenerator
from simplePipline.testing.testPipline import TestPipline


class TestLamaIndexPipeline(TestPipline):
    def __init__(self, query_engine, filepath='./data', version=0):
        super().__init__(filepath, version)
        self.query_engine = query_engine

    async def run(self):
        self.responses = await self.get_responses(self.question_dataset)

    async def run_query(self, query):
        try:
            # Await the asynchronous call
            return await self.query_engine.aquery(query)
        except:
            return Response(response="Error, query failed.")

    async def get_responses(self, questions):
        all_responses = []
        for batch_size in range(0, len(questions), 5):
            batch_qs = questions[batch_size:batch_size + 5]
            tasks = [self.run_query(q) for q in batch_qs]
            responses = await asyncio.gather(*tasks)
            all_responses.extend(responses)
            await asyncio.sleep(1)  # To avoid rate limits
        return all_responses

    async def evaluate_responses(self, evaluator, log_filename, is_correctness_evaluation=False):
        total_correct = 0
        all_results = []

        with open(log_filename, 'a') as log_file:
            for index, response in enumerate(self.responses):
                log_file.write(f"question:  {self.question_dataset[index]}  \n")
                log_file.write("response: " + response.response + "\n")
                log_file.write(f"Number of Chunks Retrived: {len(response.source_nodes)} \n")
                totallength = 0
                for node in response.source_nodes:
                    totallength += len(node.text)
                    log_file.write(f"length chunk: {len(node.text)} node score: {node.score} \n")
                    log_file.write(f" {node.text} \n\n")
                log_file.write(f"totalLength:{totallength} \n")

                if is_correctness_evaluation:
                    # For correctness evaluation, use the question along with the response
                    feedback = evaluator.evaluate_response(self.question_dataset[index], response).feedback

                else:
                    # For other evaluations, use only the response
                    feedback = evaluator.evaluate_response(response=response).feedback
                log_file.write(f"feedback: {feedback} \n \n")
                eval_result = 1 if "YES" in feedback else 0
                total_correct += eval_result
                all_results.append(eval_result)

                # if eval_result == 0:
                # log_file.write(f"No")
                # log_file.write(f" index: {index}  feedback: {feedback}\n response: {response}\n ")

        return total_correct, all_results

    async def test_pipeline(self, evaluator, log_filename, is_correctness_evaluation=False):
        total_correct, all_results = await self.evaluate_responses(evaluator, log_filename,
                                                                   is_correctness_evaluation)
        with open(log_filename, 'a') as log_file:
            log_file.write(f"Scored {total_correct} out of {len(self.question_dataset)} questions correctly.")
        print(f"Scored {total_correct} out of {len(self.question_dataset)} questions correctly.")

    async def test_hallucination(self):
        if len(self.responses) == 0:
            await self.run()
        evaluator = FaithfulnessEvaluator(service_context=self.gpt4_service_context)
        await self.test_pipeline(evaluator, f'feedback_Hallucination_{self.version}.txt')

    async def test_correction(self):
        if len(self.responses) == 0:
            await self.run()
        evaluator = QueryResponseEvaluator(service_context=self.gpt4_service_context)
        await self.test_pipeline(evaluator, f'quality_log_{self.version}.txt', True)
