import threading
from datetime import datetime
from unittest.mock import Mock, call
from uuid import UUID, uuid4

import pytest

from fiddler_evals.entities.experiment import Experiment
from fiddler_evals.pydantic_models.dataset import DatasetItem
from fiddler_evals.pydantic_models.experiment import (
    ExperimentItemResult,
    NewExperimentItem,
)
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.runner.experiment_result_publisher import ExperimentResultPublisher


@pytest.fixture
def mock_experiment():
    """Create a mock experiment for testing."""
    experiment = Mock(spec=Experiment)
    experiment.id = uuid4()
    experiment.name = "test_experiment"
    experiment.add_results = Mock()
    return experiment


@pytest.fixture
def publisher(mock_experiment):
    """Create a publisher instance for testing."""
    return ExperimentResultPublisher(experiment=mock_experiment, batch_size=3)


@pytest.fixture
def sample_result():
    """Create a sample experiment result for testing."""
    experiment_item = NewExperimentItem(
        dataset_item_id=uuid4(),
        outputs={"prediction": "test"},
        duration_ms=500,
        status="COMPLETED",
    )
    dataset_item = DatasetItem(
        id=UUID("12345678-1234-1234-1234-123456789012"),
        inputs={"question": "What happens to you if you eat watermelon seeds?"},
        expected_outputs={
            "answer": "The watermelon seeds pass through your digestive system"
        },
        metadata={},
        extras={},
        source_name="wonderopolis.org",
        source_id="1",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    score = Score(
        name="test_score",
        evaluator_name="TestEvaluator",
        value=1.0,
        label="Pass",
        status=ScoreStatus.SUCCESS,
        reasoning="Test reasoning",
    )
    return ExperimentItemResult(
        experiment_item=experiment_item, dataset_item=dataset_item, scores=[score]
    )


def test_init_default_batch_size(mock_experiment):
    """When initializing with default batch size
    Then it should use batch size of 10."""
    publisher = ExperimentResultPublisher(experiment=mock_experiment)

    assert publisher._batch_size == 10
    assert publisher._buffer == []


def test_init_custom_batch_size(mock_experiment):
    """When initializing with custom batch size
    Then it should use the specified batch size."""
    publisher = ExperimentResultPublisher(experiment=mock_experiment, batch_size=5)

    assert publisher._batch_size == 5


def test_publish_single_item_no_flush(publisher, sample_result):
    """When publishing a single item below batch size
    Then it should buffer the item without flushing."""
    publisher.publish(sample_result)

    assert len(publisher._buffer) == 1
    assert publisher._buffer[0] == sample_result
    publisher.experiment.add_results.assert_not_called()


def test_publish_reaches_batch_size_auto_flush(publisher, sample_result):
    """When publishing items that reach batch size
    Then it should automatically flush the buffer."""
    # Create multiple unique results
    results = [sample_result for _ in range(3)]

    # Publish all results
    for result in results:
        publisher.publish(result)

    # Should have flushed once and buffer should be empty
    assert len(publisher._buffer) == 0
    publisher.experiment.add_results.assert_called_once_with(items=results)


def test_publish_multiple_batches(publisher, sample_result):
    """When publishing multiple batches
    Then it should flush each batch separately."""
    # Create 6 results (2 batches of 3)
    results = [sample_result for _ in range(6)]

    # Publish all results
    for result in results:
        publisher.publish(result)

    # Should have flushed twice and buffer should be empty
    assert len(publisher._buffer) == 0
    assert publisher.experiment.add_results.call_count == 2

    # Verify the calls
    expected_calls = [call(items=results[:3]), call(items=results[3:6])]
    publisher.experiment.add_results.assert_has_calls(expected_calls)


def test_flush_empty_buffer(publisher):
    """When flushing an empty buffer
    Then it should not call add_results."""
    publisher.flush()

    publisher.experiment.add_results.assert_not_called()


def test_flush_with_buffered_items(publisher, sample_result):
    """When flushing with buffered items
    Then it should push all items and clear buffer."""
    # Add items to buffer
    publisher._buffer = [sample_result, sample_result]

    publisher.flush()

    # Should have called add_results with buffered items
    publisher.experiment.add_results.assert_called_once_with(
        items=[sample_result, sample_result]
    )
    assert len(publisher._buffer) == 0


def test_flush_after_partial_batch(publisher, sample_result):
    """When flushing after partial batch
    Then it should push remaining items."""
    # Publish 2 items (below batch size)
    publisher.publish(sample_result)
    publisher.publish(sample_result)

    # Flush manually
    publisher.flush()

    # Should have called add_results once with 2 items
    publisher.experiment.add_results.assert_called_once()
    call_args = publisher.experiment.add_results.call_args
    assert len(call_args[1]["items"]) == 2
    assert len(publisher._buffer) == 0


def test_thread_safety_concurrent_publish(mock_experiment, sample_result):
    """When publishing from multiple threads concurrently
    Then it should handle synchronization correctly."""
    publisher = ExperimentResultPublisher(experiment=mock_experiment, batch_size=10)

    # Create multiple threads publishing results
    threads = []
    num_threads = 5
    results_per_thread = 2

    def publish_results():
        for _ in range(results_per_thread):
            publisher.publish(sample_result)

    # Start all threads
    for _ in range(num_threads):
        thread = threading.Thread(target=publish_results)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Flush remaining results
    publisher.flush()

    # Should have published all results
    total_results = num_threads * results_per_thread
    assert publisher.experiment.add_results.call_count >= 1

    # Verify all results were published
    all_calls = publisher.experiment.add_results.call_args_list
    total_published = sum(len(call[1]["items"]) for call in all_calls)
    assert total_published == total_results


def test_thread_safety_concurrent_flush(mock_experiment, sample_result):
    """When flushing from multiple threads concurrently
    Then it should handle synchronization correctly."""
    publisher = ExperimentResultPublisher(experiment=mock_experiment, batch_size=10)

    # Add some items to buffer
    publisher._buffer = [sample_result, sample_result, sample_result]

    # Create multiple threads calling flush
    threads = []
    num_threads = 3

    def flush_results():
        publisher.flush()

    # Start all threads
    for _ in range(num_threads):
        thread = threading.Thread(target=flush_results)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Should have called add_results at least once
    assert publisher.experiment.add_results.call_count >= 1
    # Buffer should be empty
    assert len(publisher._buffer) == 0


def test_publish_after_flush(publisher, sample_result):
    """When publishing after a flush
    Then it should work correctly with empty buffer."""
    # Add and flush some items
    publisher.publish(sample_result)
    publisher.flush()

    # Publish more items
    publisher.publish(sample_result)

    assert len(publisher._buffer) == 1
    assert publisher._buffer[0] == sample_result


def test_multiple_flush_calls(publisher, sample_result):
    """When calling flush multiple times
    Then it should handle empty buffer gracefully."""
    # Add some items
    publisher.publish(sample_result)
    publisher.publish(sample_result)

    # Flush multiple times
    publisher.flush()
    publisher.flush()
    publisher.flush()

    # Should have called add_results only once (first flush)
    publisher.experiment.add_results.assert_called_once()
    assert len(publisher._buffer) == 0


def test_batch_size_one_immediate_flush(mock_experiment, sample_result):
    """When batch size is 1
    Then it should flush immediately on each publish."""
    publisher = ExperimentResultPublisher(experiment=mock_experiment, batch_size=1)

    # Publish 3 items
    publisher.publish(sample_result)
    publisher.publish(sample_result)
    publisher.publish(sample_result)

    # Should have flushed 3 times
    assert publisher.experiment.add_results.call_count == 3
    assert len(publisher._buffer) == 0
