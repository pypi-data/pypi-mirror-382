from fiddler_evals.evaluators.base import FiddlerEvaluator
from fiddler_evals.pydantic_models.score import Score


class Sentiment(FiddlerEvaluator):
    """Evaluator to assess text sentiment using Fiddler's sentiment analysis model.

    The Sentiment evaluator uses Fiddler's implementation of the cardiffnlp/twitter-roberta-base-sentiment-latest
    model to evaluate the sentiment polarity of text content. This evaluator helps identify
    the emotional tone and attitude expressed in text, providing both sentiment labels and
    confidence scores for sentiment classification.

    Key Features:
        - **Sentiment Classification**: Evaluates text for positive, negative, or neutral sentiment
        - **Dual Score Output**: Returns both sentiment label and probability confidence
        - **Fiddler Integration**: Leverages Fiddler's optimized sentiment evaluation model
        - **Multi-Score Output**: Returns both sentiment label and probability scores

    Sentiment Categories Evaluated:
        - **sentiment**: The predicted sentiment label (positive, negative, neutral)
        - **sentiment_prob**: Probability score (0.0-1.0) for the predicted sentiment

    Use Cases:
        - **Social Media Monitoring**: Analyzing sentiment in tweets, posts, and comments
        - **Customer Feedback Analysis**: Understanding customer satisfaction and opinions
        - **Brand Monitoring**: Tracking public sentiment about products or services
        - **Content Moderation**: Identifying emotionally charged or problematic content
        - **Market Research**: Analyzing public opinion and sentiment trends

    Scoring Logic:
        The sentiment evaluation provides two complementary scores:
        - **sentiment**: The predicted sentiment label
            - "positive": Text expresses positive emotions or opinions
            - "negative": Text expresses negative emotions or opinions
            - "neutral": Text expresses neutral or balanced sentiment
        - **sentiment_prob**: Confidence score (0.0-1.0) for the prediction
            - **0.0-0.3**: Low confidence in sentiment prediction
            - **0.3-0.7**: Medium confidence in sentiment prediction
            - **0.7-1.0**: High confidence in sentiment prediction

    Args:
        text (str): The text content to evaluate for sentiment.

    Returns:
        list[Score]: A list of Score objects containing:
            - sentiment: Score object with sentiment label (positive/negative/neutral)
            - sentiment_prob: Score object with probability score (0.0-1.0)

    Raises:
        ValueError: If the text is empty or None, or if no scores are returned from the API.

    Example:
        >>> from fiddler_evals.evaluators import Sentiment
        >>> evaluator = Sentiment()

        # Positive sentiment
        scores = evaluator.score("I love this product! It's amazing!")
        print(f"Sentiment: {scores[0].label}")
        print(f"Confidence: {scores[1].value}")
        # Sentiment: positive
        # Confidence: 0.95

        # Negative sentiment
        negative_scores = evaluator.score("This is terrible and disappointing!")
        print(f"Sentiment: {negative_scores[0].label}")
        print(f"Confidence: {negative_scores[1].value}")
        # Sentiment: negative
        # Confidence: 0.88

        # Neutral sentiment
        neutral_scores = evaluator.score("The weather is okay today.")
        print(f"Sentiment: {neutral_scores[0].label}")
        print(f"Confidence: {neutral_scores[1].value}")
        # Sentiment: neutral
        # Confidence: 0.72

        # Filter based on sentiment and confidence
        if scores[0].label == "positive" and scores[1].value > 0.8:
            print("High confidence positive sentiment detected")

    Note:
        This evaluator is optimized for social media and informal text analysis using
        the cardiffnlp/twitter-roberta-base-sentiment-latest model. It performs best on
        short, conversational text similar to Twitter posts. For formal or academic text,
        consider using specialized sentiment analysis models. The dual-score output
        provides both categorical classification and confidence assessment for robust
        sentiment analysis workflows.
    """

    name = "sentiment_analysis"

    def score(self, text: str) -> list[Score]:  # pylint: disable=arguments-differ
        """Score the sentiment of text content.

        Args:
            text (str): The text content to evaluate for sentiment.

        Returns:
            list[Score]: A list of Score objects for sentiment label and probability.
        """
        text = text.strip() if text else ""

        if not text:
            raise ValueError("text is required for sentiment evaluation")

        payload = {
            "evaluator_name": self.name,
            "parameters": {},
            "inputs": {"text": text},
        }

        return self._parse_scores(data=self.make_call(payload))
