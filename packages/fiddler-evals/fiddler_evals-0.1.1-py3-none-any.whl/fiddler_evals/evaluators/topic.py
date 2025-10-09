from typing import Any

from fiddler_evals.evaluators.base import FiddlerEvaluator
from fiddler_evals.pydantic_models.score import Score


class TopicClassification(FiddlerEvaluator):
    """Evaluator to classify text topics using Fiddler's zero-shot topic classification model.

    The TopicClassification evaluator uses Fiddler's implementation of the mortizlaurer/roberta-base-zeroshot-v2-0-c
    model to classify text content into predefined topic categories. This evaluator helps identify
    the main subject matter or theme of text content, providing both topic labels and
    confidence scores for topic classification.

    Key Features:
        - **Topic Classification**: Classifies text into predefined topic categories
        - **Dual Score Output**: Returns both topic label and probability confidence
        - **Zero-Shot Model**: Uses mortizlaurer/roberta-base-zeroshot-v2-0-c for flexible topic classification
        - **Multi-Score Output**: Returns both topic name and probability scores

    Topic Categories Evaluated:
        - **top_topic**: The predicted topic name from the provided topics list
        - **top_topic_prob**: Probability score (0.0-1.0) for the predicted topic

    Use Cases:
        - **Content Categorization**: Automatically organizing content by topic
        - **Document Classification**: Sorting documents by subject matter
        - **News Analysis**: Categorizing news articles by topic
        - **Customer Support**: Routing tickets by topic or issue type
        - **Content Moderation**: Identifying content themes for policy enforcement

    Scoring Logic:
        The topic classification provides two complementary scores:
        - **top_topic**: The predicted topic name from the provided topics list
            - Selected from the topics provided during initialization
            - Represents the most relevant topic for the input text
        - **top_topic_prob**: Confidence score (0.0-1.0) for the prediction
            - **0.0-0.3**: Low confidence in topic prediction
            - **0.3-0.7**: Medium confidence in topic prediction
            - **0.7-1.0**: High confidence in topic prediction

    Args:
        topics (list[str]): List of topic categories to classify text into.

    Returns:
        list[Score]: A list of Score objects containing:
            - top_topic: Score object with predicted topic name
            - top_topic_prob: Score object with probability score (0.0-1.0)

    Raises:
        ValueError: If the text is empty or None, or if no scores are returned from the API.

    Example:
        >>> from fiddler_evals.evaluators import TopicClassification
        >>> evaluator = TopicClassification(topics=["technology", "sports", "politics", "entertainment"])

        # Technology topic
        scores = evaluator.score("The new AI model shows promising results in natural language processing.")
        print(f"Topic: {scores[0].label}")
        print(f"Confidence: {scores[1].value}")
        # Topic: technology
        # Confidence: 0.92

        # Sports topic
        sports_scores = evaluator.score("The team won the championship with an amazing performance!")
        print(f"Topic: {sports_scores[0].label}")
        print(f"Confidence: {sports_scores[1].value}")
        # Topic: sports
        # Confidence: 0.88

        # Politics topic
        politics_scores = evaluator.score("The new policy will affect millions of citizens.")
        print(f"Topic: {politics_scores[0].label}")
        print(f"Confidence: {politics_scores[1].value}")
        # Topic: politics
        # Confidence: 0.85

        # Filter based on topic and confidence
        if scores[0].label == "technology" and scores[1].value > 0.8:
            print("High confidence technology topic detected")

    Note:
        This evaluator uses zero-shot classification, meaning it can classify text into
        any set of topics provided during initialization without requiring training data
        for those specific topics. The mortizlaurer/roberta-base-zeroshot-v2-0-c model
        is particularly effective for general-purpose topic classification across
        diverse domains. The dual-score output provides both categorical classification
        and confidence assessment for robust topic analysis workflows.
    """

    name = "topic_classification"

    def __init__(self, topics: list[str], **kwargs: Any):
        """Initialize the TopicClassification evaluator.

        Args:
            topics (list[str]): List of topic categories to classify text into.

        Raises:
            ValueError: If the topics are empty or None.
        """
        super().__init__(**kwargs)

        if not topics:
            raise ValueError("Topics are required for topic classification")

        self.topics = topics

    def score(self, text: str) -> list[Score]:  # pylint: disable=arguments-differ
        """Score the topic classification of text content.

        Args:
            text (str): The text content to evaluate for topic classification.

        Returns:
            list[Score]: A list of Score objects for topic name and probability.
        """
        text = text.strip() if text else ""

        if not text:
            raise ValueError("text is required for topic classification")

        payload = {
            "evaluator_name": self.name,
            "parameters": {"topics": self.topics},
            "inputs": {"text": text},
        }

        return self._parse_scores(data=self.make_call(payload))
