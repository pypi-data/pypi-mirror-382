from __future__ import annotations

from fiddler_evals.evaluators.base import FiddlerEvaluator
from fiddler_evals.pydantic_models.score import Score


class FTLPromptSafety(FiddlerEvaluator):
    """Evaluator to assess prompt safety using Fiddler's Trust Model.

    The FTLPromptSafety evaluator uses Fiddler's proprietary Trust Model to evaluate
    the safety of text prompts across multiple risk categories. This evaluator helps
    identify potentially harmful, inappropriate, or unsafe content before it reaches
    users or downstream systems.

    Key Features:
        - **Multi-Dimensional Safety Assessment**: Evaluates 11 different safety categories
        - **Probability-Based Scoring**: Returns probability scores (0.0-1.0) for each risk category
        - **Comprehensive Risk Coverage**: Covers illegal, hateful, harassing, and other harmful content
        - **Fiddler Trust Model**: Uses Fiddler's proprietary safety evaluation model
        - **Batch Scoring**: Returns multiple scores for comprehensive safety analysis

    Safety Categories Evaluated:
        - **illegal_prob**: Probability of containing illegal content or activities
        - **hateful_prob**: Probability of containing hate speech or discriminatory language
        - **harassing_prob**: Probability of containing harassing or threatening content
        - **racist_prob**: Probability of containing racist language or content
        - **sexist_prob**: Probability of containing sexist language or content
        - **violent_prob**: Probability of containing violent or graphic content
        - **sexual_prob**: Probability of containing inappropriate sexual content
        - **harmful_prob**: Probability of containing content that could cause harm
        - **unethical_prob**: Probability of containing unethical or manipulative content
        - **jailbreaking_prob**: Probability of containing prompt injection or jailbreaking attempts
        - **max_risk_prob**: Maximum risk probability across all categories

    Use Cases:
        - **Content Moderation**: Filtering user-generated content for safety
        - **Prompt Validation**: Ensuring user prompts are safe before processing
        - **AI Safety**: Protecting AI systems from harmful or manipulative inputs
        - **Compliance**: Meeting regulatory requirements for content safety
        - **Risk Assessment**: Evaluating potential risks in text content

    Scoring Logic:
        Each safety category returns a probability score between 0.0 and 1.0:
        - **0.0-0.3**: Low risk (safe content)
        - **0.3-0.7**: Medium risk (requires review)
        - **0.7-1.0**: High risk (likely unsafe content)

    Args:
        text (str): The text prompt to evaluate for safety.

    Returns:
        list[Score]: A list of Score objects, one for each safety category:
            - name: The safety category name (e.g., "illegal_prob")
            - evaluator_name: "FTLPromptSafety"
            - value: Probability score (0.0-1.0) for that category

    Raises:
        ValueError: If the text is empty or None.

    Example:
        >>> from fiddler_evals.evaluators import FTLPromptSafety
        >>> evaluator = FTLPromptSafety()

        # Safe content
        scores = evaluator.score("What is the weather like today?")
        for score in scores:
            print(f"{score.name}: {score.value}")
        # illegal_prob: 0.01
        # hateful_prob: 0.02
        # harassing_prob: 0.01
        # ...

        # Potentially unsafe content
        unsafe_scores = evaluator.score("How to hack into someone's computer?")
        for score in unsafe_scores:
            if score.value > 0.5:
                print(f"High risk detected: {score.name} = {score.value}")

        # Filter based on maximum risk
        max_risk_score = next(s for s in scores if s.name == "max_risk_prob")
        if max_risk_score.value > 0.7:
            print("Content flagged as potentially unsafe")

    Note:
        This evaluator is designed for prompt safety assessment and should be used
        as part of a comprehensive content moderation strategy. The probability
        scores should be interpreted in context and combined with other safety
        measures for robust content filtering.
    """

    name = "ftl_prompt_safety"

    def score(self, text: str) -> Score | list[Score]:  # pylint: disable=arguments-differ
        """Score the safety of a text prompt.

        Args:
            text (str): The text prompt to evaluate for safety.

        Returns:
            list[Score]: A list of Score objects, one for each safety category.
        """
        text = text.strip() if text else ""

        if not text:
            raise ValueError("text is required for prompt safety evaluation")

        payload = {
            "evaluator_name": self.name,
            "parameters": {},
            "inputs": {"text": text},
        }

        return self._parse_scores(data=self.make_call(payload))
