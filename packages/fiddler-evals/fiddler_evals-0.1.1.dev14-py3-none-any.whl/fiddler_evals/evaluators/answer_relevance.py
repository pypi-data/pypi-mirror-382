from fiddler_evals.evaluators.base import FiddlerEvaluator
from fiddler_evals.pydantic_models.score import Score


class AnswerRelevance(FiddlerEvaluator):
    """Evaluator to assess how well an answer addresses a given question.

    The AnswerRelevance evaluator measures whether an LLM's answer is relevant
    and directly addresses the question being asked. This is a critical metric
    for ensuring that LLM responses stay on topic and provide meaningful value
    to users.

    Key Features:
        - **Relevance Assessment**: Determines if the answer directly addresses the question
        - **Binary Scoring**: Returns 1.0 for relevant answers, 0.0 for irrelevant ones
        - **Detailed Reasoning**: Provides explanation for the relevance assessment
        - **Fiddler API Integration**: Uses Fiddler's built-in relevance evaluation model

    Use Cases:
        - **Q&A Systems**: Ensuring answers stay on topic
        - **Customer Support**: Verifying responses address user queries
        - **Educational Content**: Checking if explanations answer the question
        - **Research Assistance**: Validating that responses are relevant to queries

    Scoring Logic:
        - **1.0 (Relevant)**: Answer directly addresses the question with relevant information
        - **0.0 (Irrelevant)**: Answer doesn't address the question or goes off-topic

    Args:
        prompt (str): The question being asked.
        response (str): The LLM's response to evaluate.

    Returns:
        Score: A Score object containing:
            - value: 1.0 if relevant, 0.0 if irrelevant
            - label: String representation of the boolean result
            - reasoning: Detailed explanation of the assessment

    Example:
        >>> from fiddler_evals.evaluators import AnswerRelevance
        >>> evaluator = AnswerRelevance()

        # Relevant answer
        score = evaluator.score(
            prompt="What is the capital of France?",
            response="The capital of France is Paris."
        )
        print(f"Relevance: {score.value}")  # 1.0
        print(f"Reasoning: {score.reasoning}")

        # Irrelevant answer
        score = evaluator.score(
            question="What is the capital of France?",
            answer="I like pizza and Italian food."
        )
        print(f"Relevance: {score.value}")  # 0.0

    Note:
        This evaluator uses Fiddler's built-in relevance assessment model
        and requires an active connection to the Fiddler API.
    """

    name = "answer_relevance"

    def score(self, prompt: str, response: str) -> Score:  # pylint: disable=arguments-differ
        """Score the relevance of an answer to a question.

        Args:
            prompt (str): The question being asked.
            response (str): The LLM's response to evaluate.

        Returns:
            Score: A Score object containing:
                - value: 1.0 if relevant, 0.0 if irrelevant
                - label: String representation of the boolean result
                - reasoning: Detailed explanation of the assessment
        """
        prompt = prompt.strip() if prompt else ""
        response = response.strip() if response else ""

        if not prompt or not response:
            raise ValueError(
                "prompt and response are required for relevance evaluation"
            )

        payload = {
            "evaluator_name": self.name,
            "parameters": {},
            "inputs": {"prompt": prompt, "response": response},
        }

        return self._parse_scores(data=self.make_call(payload))[0]
