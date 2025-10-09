from fiddler_evals.evaluators.base import FiddlerEvaluator
from fiddler_evals.pydantic_models.score import Score


class Toxicity(FiddlerEvaluator):
    """Evaluator to assess text toxicity using Fiddler's unbiased toxicity model.

    The Toxicity evaluator uses Fiddler's implementation of the unitary/unbiased-toxic-roberta
    model to evaluate the toxicity level of text content. This evaluator helps identify
    potentially harmful, offensive, or inappropriate language in text, providing a probability
    score for toxicity assessment.

    Key Features:
        - **Toxicity Assessment**: Evaluates text for toxic, harmful, or offensive content
        - **Probability-Based Scoring**: Returns probability scores (0.0-1.0) for toxicity
        - **Unbiased Model**: Uses unitary/unbiased-toxic-roberta for fair toxicity detection
        - **Fiddler Integration**: Leverages Fiddler's optimized toxicity evaluation model
        - **Single Score Output**: Returns a single toxicity probability score

    Toxicity Categories Evaluated:
        - **toxicity_prob**: Probability that the text contains toxic content

    Use Cases:
        - **Content Moderation**: Filtering user-generated content for toxicity
        - **Social Media Monitoring**: Detecting harmful language in posts and comments
        - **Chatbot Safety**: Ensuring AI responses are not toxic or offensive
        - **Community Guidelines**: Enforcing platform policies on appropriate language
        - **Content Filtering**: Automatically flagging potentially harmful content

    Scoring Logic:
        The toxicity score represents the probability that the text contains toxic content:
        - **0.0-0.3**: Low toxicity (likely safe content)
        - **0.3-0.7**: Medium toxicity (may contain some harmful language)
        - **0.7-1.0**: High toxicity (likely contains toxic or offensive content)

    Args:
        text (str): The text content to evaluate for toxicity.

    Returns:
        Score: A Score object containing:
            - name: The toxicity category name ("toxicity_prob")
            - evaluator_name: "Toxicity"
            - value: Probability score (0.0-1.0) for toxicity

    Raises:
        ValueError: If the text is empty or None, or if no scores are returned from the API.

    Example:
        >>> from fiddler_evals.evaluators import Toxicity
        >>> evaluator = Toxicity()

        # Safe content
        score = evaluator.score("Hello, how are you today?")
        print(f"Toxicity: {score.value}")
        # Toxicity: 0.02

        # Potentially toxic content
        toxic_score = evaluator.score("This is absolutely terrible and offensive!")
        print(f"Toxicity: {toxic_score.value}")
        # Toxicity: 0.75

        # Highly toxic content
        very_toxic_score = evaluator.score("You are a worthless piece of garbage!")
        print(f"Toxicity: {very_toxic_score.value}")
        # Toxicity: 0.95

        # Filter based on toxicity threshold
        if score.value > 0.7:
            print("Content flagged as potentially toxic")

    Note:
        This evaluator is designed for toxicity assessment and should be used as part
        of a comprehensive content moderation strategy. The probability scores should
        be interpreted in context and combined with other safety measures for robust
        content filtering. The model is trained to be unbiased and fair across
        different demographics and contexts.
    """

    name = "toxicity"

    def score(self, text: str) -> Score:  # pylint: disable=arguments-differ
        """Score the toxicity of text content.

        Args:
            text (str): The text content to evaluate for toxicity.

        Returns:
            Score: A Score object for toxicity probability.
        """
        text = text.strip() if text else ""

        if not text:
            raise ValueError("text is required for toxicity evaluation")

        payload = {
            "evaluator_name": self.name,
            "parameters": {},
            "inputs": {"text": text},
        }

        return self._parse_scores(data=self.make_call(payload))[0]
