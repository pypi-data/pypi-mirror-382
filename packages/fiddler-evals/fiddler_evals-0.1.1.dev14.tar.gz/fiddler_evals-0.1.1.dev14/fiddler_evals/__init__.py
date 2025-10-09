from contextvars import ContextVar
from typing import TYPE_CHECKING

from fiddler_evals.connection import init
from fiddler_evals.entities.application import Application
from fiddler_evals.entities.dataset import Dataset
from fiddler_evals.entities.experiment import (
    Experiment,
    ExperimentItemStatus,
    ExperimentStatus,
)
from fiddler_evals.entities.project import Project
from fiddler_evals.evaluators import (
    AnswerRelevance,
    Coherence,
    Conciseness,
    FTLPromptSafety,
    FTLResponseFaithfulness,
    RegexMatch,
    RegexSearch,
    Sentiment,
    TopicClassification,
    Toxicity,
)
from fiddler_evals.evaluators.base import Evaluator
from fiddler_evals.evaluators.eval_fn import EvalFn
from fiddler_evals.pydantic_models.dataset import DatasetItem, NewDatasetItem
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.runner.evaluation import evaluate
from fiddler_evals.version import __version__

if TYPE_CHECKING:
    from fiddler_evals.connection import Connection

# ContextVar to store the connection object and reuse it while making API calls.
connection_context: ContextVar["Connection | None"] = ContextVar(
    "connection", default=None
)

__all__ = [
    "__version__",
    "init",
    # Entities
    "Application",
    "Project",
    "Dataset",
    "Experiment",
    # Core data models
    "NewDatasetItem",
    "DatasetItem",
    "Score",
    # Evaluator system
    "Evaluator",
    "EvalFn",
    "AnswerRelevance",
    "Coherence",
    "Conciseness",
    "Toxicity",
    "Sentiment",
    "RegexSearch",
    "RegexMatch",
    "FTLPromptSafety",
    "FTLResponseFaithfulness",
    "TopicClassification",
    # Top level methods
    "evaluate",
    # Status enums
    "ExperimentStatus",
    "ExperimentItemStatus",
    "ScoreStatus",
]
