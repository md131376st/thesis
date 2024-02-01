import logging

from llama_index import Response

from llama_index.llms import OpenAI

from llama_index import ServiceContext
from llama_index.evaluation import FaithfulnessEvaluator, QueryResponseEvaluator

import os
import asyncio

from simplePipline.Loader.documentLoader import DocumentLoader
from simplePipline.test.questionGenrator import QuestionGenerator
from simplePipline.test.testPipline import TestPipline
from simplePipline.utils.logger import Logger


class TestLamaIndexPipeline(TestPipline):
    def __init__(self, query_engine, filepath='./data', version=0, loglevel=logging.INFO):
        super().__init__(filepath, version)
        self.query_engine = query_engine
        self.loglevel = loglevel

    async def run(self):
        self.responses = await self.get_responses()

    async def run_query(self, query):
        try:
            # Await the asynchronous call
            return await self.query_engine.aquery(query)
        except:
            return Response(response="Error, query failed.")

    async def get_responses(self):
        all_responses = []
        for batch_size in range(0, len(self.question_dataset), 5):
            batch_qs = self.question_dataset[batch_size:batch_size + 5]
            tasks = [self.run_query(q) for q in batch_qs]
            responses = await asyncio.gather(*tasks)
            all_responses.extend(responses)
            await asyncio.sleep(1)  # To avoid rate limits
        return all_responses

    async def evaluate_responses(self, evaluator, logger, is_correctness_evaluation=False):
        total_correct = 0
        all_results = []

        for index, response in enumerate(self.responses):

            logger.debug(f"question:  {self.question_dataset[index]}  \n")
            logger.debug("response: " + response.response + "\n")
            logger.debug(f"Number of Chunks Retrived: {len(response.source_nodes)} \n")
            totallength = 0
            for node in response.source_nodes:
                totallength += len(node.text)
                logger.debug(f"length chunk: {len(node.text)} node score: {node.score} \n")
                logger.debug(f" {node.text} \n\n")
            logger.debug(f"totalLength:{totallength} \n")

            if is_correctness_evaluation:
                # For correctness evaluation, use the question along with the response
                feedback = evaluator.evaluate_response(self.question_dataset[index], response).feedback

            else:
                # For other evaluations, use only the response
                feedback = evaluator.evaluate_response(response=response).feedback
            logger.debug(f"feedback: {feedback} \n \n")
            eval_result = 1 if "YES" in feedback else 0
            total_correct += eval_result
            all_results.append(eval_result)

        return total_correct, all_results

    async def test_pipeline(self, evaluator, logger, is_correctness_evaluation=False):
        logger.info("start test \n")
        total_correct, all_results = await self.evaluate_responses(evaluator,
                                                                   logger,
                                                                   is_correctness_evaluation)

        logger.info(f"Scored {total_correct} out of {len(self.question_dataset)} questions correctly.")

    async def test_hallucination(self):
        if len(self.responses) == 0:
            await self.run()
        evaluator = FaithfulnessEvaluator(service_context=self.gpt4_service_context)
        logger = Logger("TestLamaIndexPipeline",
                        f'feedback_Hallucination_{self.version}.txt',
                        level=self.loglevel).get_logger()
        await self.test_pipeline(evaluator, logger)

    async def test_correction(self):
        if len(self.responses) == 0:
            await self.run()
        evaluator = QueryResponseEvaluator(service_context=self.gpt4_service_context)
        logger = Logger("TestLamaIndexPipeline",
                        f'quality_log_{self.version}.txt',
                        level=self.loglevel).get_logger()
        await self.test_pipeline(evaluator, logger, True)
