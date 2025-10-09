from fiddler_evals.evaluators.base import FiddlerEvaluator
from fiddler_evals.pydantic_models.score import Score


class Conciseness(FiddlerEvaluator):
    """Evaluator to assess how concise and to-the-point an answer is.

    The Conciseness evaluator measures whether an LLM's answer is appropriately
    brief and direct without unnecessary verbosity. This metric is important for
    ensuring that responses are efficient and don't waste users' time with
    irrelevant details or excessive elaboration.

    Key Features:
        - **Conciseness Assessment**: Determines if the answer is appropriately brief
        - **Binary Scoring**: Returns 1.0 for concise answers, 0.0 for verbose ones
        - **Detailed Reasoning**: Provides explanation for the conciseness assessment
        - **Fiddler API Integration**: Uses Fiddler's built-in conciseness evaluation model

    Use Cases:
        - **Customer Support**: Ensuring responses are direct and helpful
        - **Technical Documentation**: Verifying explanations are clear and brief
        - **Educational Content**: Checking if explanations are appropriately detailed
        - **API Responses**: Ensuring responses are efficient and focused

    Scoring Logic:
        - **1.0 (Concise)**: Answer is appropriately brief and to-the-point
        - **0.0 (Verbose)**: Answer is unnecessarily long or contains irrelevant details

    Args:
        response (str): The LLM's response to evaluate for conciseness.

    Returns:
        Score: A Score object containing:
            - value: 1.0 if concise, 0.0 if verbose
            - label: String representation of the boolean result
            - reasoning: Detailed explanation of the assessment

    Example:
        >>> from fiddler_evals.evaluators import Conciseness
        >>> evaluator = Conciseness()

        # Concise answer
        score = evaluator.score("The capital of France is Paris.")
        print(f"Conciseness: {score.value}")  # 1.0
        print(f"Reasoning: {score.reasoning}")

        # Verbose answer
        score = evaluator.score(
            "Well, that's a great question about France. Let me think about this..."
            "France is a beautiful country in Europe, and it has many wonderful cities..."
            "The capital city of France is Paris, which is located in the north-central part..."
        )
        print(f"Conciseness: {score.value}")  # 0.0

    Note:
        This evaluator uses Fiddler's built-in conciseness assessment model
        and requires an active connection to the Fiddler API.
    """

    name = "conciseness"

    def score(self, response: str) -> Score:  # pylint: disable=arguments-differ
        """Score the conciseness of an answer.

        Args:
            response (str): The LLM's response to evaluate for conciseness.

        Returns:
            Score: A Score object containing:
                - value: 1.0 if concise, 0.0 if verbose
                - label: String representation of the boolean result
                - reasoning: Detailed explanation of the assessment
        """
        response = response.strip() if response else ""
        if not response:
            raise ValueError("response is required for conciseness evaluation")

        payload = {
            "evaluator_name": self.name,
            "parameters": {},
            "inputs": {"response": response},
        }

        return self._parse_scores(data=self.make_call(payload))[0]
