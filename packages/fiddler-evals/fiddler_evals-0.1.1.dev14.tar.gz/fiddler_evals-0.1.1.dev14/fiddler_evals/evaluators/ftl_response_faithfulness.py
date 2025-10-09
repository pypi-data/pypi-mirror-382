from fiddler_evals.evaluators.base import FiddlerEvaluator
from fiddler_evals.pydantic_models.score import Score


class FTLResponseFaithfulness(FiddlerEvaluator):
    """Evaluator to assess response faithfulness using Fiddler's Trust Model.

    The FTLResponseFaithfulness evaluator uses Fiddler's proprietary Trust Model to evaluate
    how faithful an LLM response is to the provided context. This evaluator helps ensure
    that responses accurately reflect the information in the source context and don't
    contain hallucinated or fabricated information.

    Key Features:
        - **Faithfulness Assessment**: Evaluates how well the response reflects the context
        - **Probability-Based Scoring**: Returns probability scores (0.0-1.0) for faithfulness
        - **Context-Response Alignment**: Compares response against provided context
        - **Fiddler Trust Model**: Uses Fiddler's proprietary faithfulness evaluation model
        - **Hallucination Detection**: Identifies responses that go beyond the context

    Faithfulness Categories Evaluated:
        - **faithful_prob**: Probability that the response is faithful to the context

    Use Cases:
        - **RAG Systems**: Ensuring responses stay grounded in retrieved context
        - **Document Q&A**: Verifying answers are based on provided documents
        - **Fact-Checking**: Validating that responses don't contain fabricated information
        - **Content Validation**: Ensuring responses accurately reflect source material
        - **Hallucination Detection**: Identifying responses that go beyond the context

    Scoring Logic:
        The faithfulness score represents the probability that the response is faithful to the context:
        - **0.0-0.3**: Low faithfulness (likely contains hallucinated information)
        - **0.3-0.7**: Medium faithfulness (some information may not be grounded)
        - **0.7-1.0**: High faithfulness (response accurately reflects context)

    Args:
        response (str): The LLM response to evaluate for faithfulness.
        context (str): The source context that the response should be faithful to.

    Returns:
        list[Score]: A list of Score objects containing:
            - name: The faithfulness category name ("faithful_prob")
            - evaluator_name: "FTLResponseFaithfulness"
            - value: Probability score (0.0-1.0) for faithfulness

    Raises:
        ValueError: If the response or context is empty or None.

    Example:
        >>> from fiddler_evals.evaluators import FTLResponseFaithfulness
        >>> evaluator = FTLResponseFaithfulness()

        # Faithful response
        context = "The capital of France is Paris. It is located in northern Europe."
        response = "Paris is the capital of France."
        scores = evaluator.score(response=response, context=context)
        for score in scores:
            print(f"{score.name}: {score.value}")
        # faithful_prob: 0.95

        # Unfaithful response with hallucination
        context = "The capital of France is Paris."
        response = "The capital of France is Paris, and it has a population of 2.1 million people."
        scores = evaluator.score(response=response, context=context)
        for score in scores:
            print(f"{score.name}: {score.value}")
        # faithful_prob: 0.65 (population info not in context)

        # Highly unfaithful response
        context = "The capital of France is Paris."
        response = "The capital of France is London."
        scores = evaluator.score(response=response, context=context)
        for score in scores:
            print(f"{score.name}: {score.value}")
        # faithful_prob: 0.05

        # Filter based on faithfulness threshold
        faithful_score = next(s for s in scores if s.name == "faithful_prob")
        if faithful_score.value < 0.7:
            print("Response flagged as potentially unfaithful")

    Note:
        This evaluator is designed for response faithfulness assessment and should be used
        in conjunction with other evaluation metrics for comprehensive response quality
        assessment. The probability scores should be interpreted in context and combined
        with other quality measures for robust response validation.
    """

    name = "ftl_response_faithfulness"

    def score(self, response: str, context: str) -> Score:  # pylint: disable=arguments-differ
        """Score the faithfulness of a response to its context.

        Args:
            response (str): The LLM response to evaluate for faithfulness.
            context (str): The source context that the response should be faithful to.

        Returns:
            Score: A Score object for faithfulness probability.
        """
        response = response.strip() if response else ""
        context = context.strip() if context else ""

        if not response or not context:
            raise ValueError(
                "response and context are required for faithfulness evaluation"
            )

        payload = {
            "evaluator_name": self.name,
            "parameters": {},
            "inputs": {"response": response, "context": context},
        }

        return self._parse_scores(data=self.make_call(payload))[0]
