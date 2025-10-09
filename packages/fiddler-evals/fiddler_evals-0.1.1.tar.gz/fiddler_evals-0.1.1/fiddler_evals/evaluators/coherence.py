from __future__ import annotations

from fiddler_evals.evaluators.base import FiddlerEvaluator
from fiddler_evals.pydantic_models.score import Score


class Coherence(FiddlerEvaluator):
    """Evaluator to assess the coherence and logical flow of a response.

    The Coherence evaluator measures whether a response is well-structured, logically
    consistent, and flows naturally from one idea to the next. This metric is important
    for ensuring that responses are easy to follow and understand, with clear connections
    between different parts of the text.

    Key Features:
        - **Coherence Assessment**: Determines if the response has logical flow and structure
        - **Binary Scoring**: Returns 1.0 for coherent responses, 0.0 for incoherent ones
        - **Optional Context**: Can optionally use a prompt for context-aware evaluation
        - **Detailed Reasoning**: Provides explanation for the coherence assessment
        - **Fiddler API Integration**: Uses Fiddler's built-in coherence evaluation model

    Use Cases:
        - **Content Quality**: Ensuring responses are well-structured and logical
        - **Educational Content**: Verifying explanations flow logically
        - **Technical Documentation**: Checking if instructions are coherent
        - **Creative Writing**: Assessing narrative flow and consistency
        - **Conversational AI**: Ensuring responses make sense in context

    Scoring Logic:
        - **1.0 (Coherent)**: Response has clear logical flow and structure
        - **0.0 (Incoherent)**: Response lacks logical flow or has structural issues

    Args:
        response (str): The response to evaluate for coherence.
        prompt (str, optional): The original prompt that generated the response.
                               Used for context-aware coherence evaluation.

    Returns:
        Score: A Score object containing:
            - name: "is_coherent"
            - evaluator_name: "Coherence"
            - value: 1.0 if coherent, 0.0 if incoherent
            - label: String representation of the boolean result
            - reasoning: Explanation for the coherence assessment

    Raises:
        ValueError: If the response is empty or None, or if no scores are returned from the API.

    Example:
        >>> from fiddler_evals.evaluators import Coherence
        >>> evaluator = Coherence()

        # Coherent response
        score = evaluator.score(
            response="First, we need to understand the problem. Then, we can identify potential solutions. Finally, we should test our approach."
        )
        print(f"Coherence: {score.value}")  # 1.0

        # Incoherent response
        incoherent_score = evaluator.score(
            response="The sky is blue. I like pizza. Quantum physics is complex. Let's go shopping."
        )
        print(f"Coherence: {incoherent_score.value}")  # 0.0

        # With context
        contextual_score = evaluator.score(
            prompt="Explain the process of making coffee",
            response="First, grind the beans. Then, heat the water. Next, pour water over grounds. Finally, enjoy your coffee."
        )
        print(f"Coherence: {contextual_score.value}")  # 1.0

        # Check coherence
        if score.value == 1.0:
            print("Response is coherent and well-structured")

    Note:
        This evaluator uses Fiddler's built-in coherence assessment model
        and requires an active connection to the Fiddler API. The optional
        prompt parameter can provide additional context for more accurate
        coherence evaluation, especially when the response needs to be
        evaluated in relation to a specific question or task.
    """

    name = "coherence"

    def score(self, response: str, prompt: str | None = None) -> Score:  # pylint: disable=arguments-differ
        """Score the coherence of a response.

        Args:
            response (str): The response to evaluate for coherence.
            prompt (str, optional): The original prompt that generated the response.

        Returns:
            Score: A Score object for coherence assessment.
        """
        response = response.strip() if response else ""
        prompt = prompt.strip() if prompt else ""

        if not response:
            raise ValueError("response is required for coherence evaluation")

        # Build inputs dictionary
        inputs = {"response": response, "prompt": prompt}

        payload = {
            "evaluator_name": self.name,
            "parameters": {},
            "inputs": inputs,
        }

        return self._parse_scores(data=self.make_call(payload))[0]
