"""Tests for hf base.py"""

import pytest
import typing
from hf.base import (
    HfDatasets,
    HfModels,
    HfSpaces,
    HfPapers,
    RepoType,
    list_local_repos,
    ensure_id,
    get_size,
    repo_type_helpers,
)
from huggingface_hub.hf_api import DatasetInfo, ModelInfo, SpaceInfo, PaperInfo


def test_ensure_id():
    """Test the ensure_id function with different input types."""
    # Test with string
    assert ensure_id("some/repo") == "some/repo"

    # Test with DatasetInfo - create a real one or mock properly
    # For now, just test the error case

    # Test with invalid type
    with pytest.raises(ValueError):
        ensure_id(123)


def test_repo_type_helpers_ssot():
    """Test that the repo_type_helpers SSOT configuration is correct."""
    expected_types = {"dataset", "model", "space", "paper"}
    assert set(repo_type_helpers.keys()) == expected_types

    # Check each config has required keys
    for repo_type, config in repo_type_helpers.items():
        assert "loader_func" in config
        assert "search_func" in config
        assert callable(config["loader_func"])
        assert callable(config["search_func"])


def test_hf_datasets_class_attributes():
    """Test that HfDatasets has the correct class attributes."""
    from hf.base import RepoType

    assert HfDatasets.repo_type == RepoType.DATASET

    # Test that instance has the configured functions
    d = HfDatasets()
    assert hasattr(d, "loader_func")
    assert hasattr(d, "search_func")
    assert d.loader_func is not None
    assert d.search_func is not None


def test_hf_models_class_attributes():
    """Test that HfModels has the correct class attributes."""
    from hf.base import RepoType

    assert HfModels.repo_type == RepoType.MODEL

    # Test that instance has the configured functions
    m = HfModels()
    assert hasattr(m, "loader_func")
    assert hasattr(m, "search_func")
    assert m.loader_func is not None
    assert m.search_func is not None


def test_hf_spaces_class_attributes():
    """Test that HfSpaces has the correct class attributes."""
    from hf.base import RepoType

    assert HfSpaces.repo_type == RepoType.SPACE

    # Test that instance has the configured functions
    s = HfSpaces()
    assert hasattr(s, "loader_func")
    assert hasattr(s, "search_func")
    assert s.loader_func is not None
    assert s.search_func is not None


def test_hf_papers_class_attributes():
    """Test that HfPapers has the correct class attributes."""
    from hf.base import RepoType

    assert HfPapers.repo_type == RepoType.PAPER

    # Test that instance has the configured functions
    p = HfPapers()
    assert hasattr(p, "loader_func")
    assert hasattr(p, "search_func")
    assert p.loader_func is not None
    assert p.search_func is not None


def test_hf_datasets_instance():
    """Test basic HfDatasets functionality."""
    d = HfDatasets()

    # Test that it's iterable (even if empty)
    list(d)  # Should not raise an error

    # Test length
    len(d)  # Should not raise an error

    # Test _keys method
    keys = d._keys()
    assert isinstance(keys, list)


def test_hf_models_instance():
    """Test basic HfModels functionality."""
    m = HfModels()

    # Test that it's iterable (even if empty)
    list(m)  # Should not raise an error

    # Test length
    len(m)  # Should not raise an error

    # Test _keys method
    keys = m._keys()
    assert isinstance(keys, list)


def test_hf_spaces_instance():
    """Test basic HfSpaces functionality."""
    s = HfSpaces()

    # Test that it's iterable (even if empty)
    list(s)  # Should not raise an error

    # Test length
    len(s)  # Should not raise an error

    # Test _keys method
    keys = s._keys()
    assert isinstance(keys, list)


def test_hf_papers_instance():
    """Test basic HfPapers functionality."""
    p = HfPapers()

    # Test that it's iterable (even if empty)
    list(p)  # Should not raise an error

    # Test length
    len(p)  # Should not raise an error

    # Test _keys method
    keys = p._keys()
    assert isinstance(keys, list)


def test_list_local_repos():
    """Test the list_local_repos function."""
    # Should return lists for all repo types
    datasets = list_local_repos("dataset")
    models = list_local_repos("model")
    spaces = list_local_repos("space")
    papers = list_local_repos("paper")

    assert isinstance(datasets, list)
    assert isinstance(models, list)
    assert isinstance(spaces, list)
    assert isinstance(papers, list)


def test_get_size_function_signature():
    """Test that get_size has the correct signature and default parameters."""
    import inspect

    sig = inspect.signature(get_size)

    # Should have repo_id as positional, unit_bytes and repo_type as keyword-only
    params = list(sig.parameters.keys())
    assert "repo_id" in params
    assert "unit_bytes" in params
    assert "repo_type" in params

    # repo_type should have None as default
    assert sig.parameters["repo_type"].default is None

    # unit_bytes should have a default value
    assert sig.parameters["unit_bytes"].default is not None


def test_hf_mapping_get_size_methods():
    """Test that all HfMapping subclasses have get_size methods."""
    d = HfDatasets()
    m = HfModels()
    s = HfSpaces()
    p = HfPapers()

    # Should have get_size methods
    for instance in [d, m, s, p]:
        assert hasattr(instance, "get_size")
        assert callable(instance.get_size)


def test_datasets_integration():
    """
    Integration test for HfDatasets covering searching, downloading,
    sizing, and local dataset management.
    """
    d = HfDatasets()

    key1 = "llamafactory/tiny-supervised-dataset"
    key2 = "ucirvine/sms_spam"

    # Test the get_size function (does NOT download the data)
    assert round(get_size(key1), 4) == 0.0001
    # Get size in bytes
    assert get_size(key2, unit_bytes=1) == 365026.0

    # Test search functionality
    search_results = list(d.search("tiny", limit=10))
    assert len(search_results) > 0
    assert any("tiny" in result.id.lower() for result in search_results)

    # Test download and load
    val1 = d[key1]

    # Test __contains__ - now we should have the key1 in local cache
    assert key1 in d

    # Test the contents of val1 are as expected
    assert list(val1) == ["train"]
    assert list(val1["train"].features) == ["instruction", "input", "output"]
    assert val1["train"].num_rows == 300

    # Test that the dataset is now in local listings
    local_datasets = list(d)
    assert key1 in local_datasets

    # Test instance get_size method (should use dataset repo_type automatically)
    size_via_instance = d.get_size(key1)
    assert round(size_via_instance, 4) == 0.0001


def test_models_integration():
    """
    Integration test for HfModels covering searching, downloading,
    and local model management.
    """
    m = HfModels()

    model_key = "lysandre/test-model"

    # Test the get_size function for a model
    model_size = get_size(model_key, repo_type="model")
    assert isinstance(model_size, float)
    assert model_size > 0

    # Test search functionality
    search_results = list(m.search("test", limit=10))
    assert len(search_results) > 0
    assert any("test" in result.id.lower() for result in search_results)

    # Test download - this returns the path to the downloaded model
    model_path = m[model_key]
    assert isinstance(model_path, str)
    assert model_path  # Should be non-empty

    # Test __contains__ - now we should have the model in local cache
    assert model_key in m

    # Test that the model is now in local listings
    local_models = list(m)
    assert model_key in local_models

    # Test instance get_size method (should use model repo_type automatically)
    size_via_instance = m.get_size(model_key)
    assert isinstance(size_via_instance, float)
    assert size_via_instance > 0


def test_cross_type_get_size():
    """Test get_size with auto-detection across model and dataset types."""
    # Test with a known dataset
    dataset_size = get_size("ucirvine/sms_spam")  # Auto-detection should work
    assert dataset_size == 365026.0 / (1024**3)  # Default unit is GiB

    # Test with a known model
    model_size = get_size("lysandre/test-model")  # Auto-detection should work
    assert isinstance(model_size, float)
    assert model_size > 0

    # Test explicit repo_type specification
    explicit_dataset_size = get_size("ucirvine/sms_spam", repo_type="dataset")
    assert explicit_dataset_size == dataset_size

    explicit_model_size = get_size("lysandre/test-model", repo_type="model")
    assert explicit_model_size == model_size


def test_get_size_paper_error():
    """Test that get_size raises appropriate error for papers."""
    with pytest.raises(ValueError, match="Papers don't have file sizes"):
        get_size("some_paper_id", repo_type="paper")


def test_spaces_and_papers_integration():
    """
    Integration test for HfSpaces and HfPapers covering searching and info retrieval.
    """
    s = HfSpaces()
    p = HfPapers()

    # Test space search functionality - just check we get results
    space_search_results = list(s.search("demo", limit=5))
    assert len(space_search_results) > 0

    # Test paper search functionality
    paper_search_results = list(p.search("transformer", limit=5))
    assert len(paper_search_results) > 0
    # Check that at least one result has 'transformer' in title or abstract
    has_transformer = any(
        "transformer" in getattr(result, "title", "").lower()
        or "transformer" in getattr(result, "summary", "").lower()
        for result in paper_search_results
    )
    assert has_transformer

    # Test accessing specific items (if they exist)
    if space_search_results:
        first_space = space_search_results[0]
        space_info = s[first_space.id]
        assert space_info is not None
        assert hasattr(space_info, "id")

    if paper_search_results:
        first_paper = paper_search_results[0]
        paper_info = p[first_paper.id]
        assert paper_info is not None
        assert hasattr(paper_info, "id")


def test_repo_type_enum():
    """Test that RepoType enum matches repo_type_helpers keys and supports both enum and string access."""
    from hf.base import RepoType

    # Check that RepoType enum values match repo_type_helpers keys
    enum_values = [rt.value for rt in RepoType]
    assert set(enum_values) == set(repo_type_helpers.keys())

    # Check specific expected values
    expected_types = {"dataset", "model", "space", "paper"}
    assert set(enum_values) == expected_types

    # Test that enum supports string comparison (str, Enum inheritance)
    assert RepoType.DATASET == "dataset"
    assert RepoType.MODEL == "model"
    assert RepoType.SPACE == "space"
    assert RepoType.PAPER == "paper"

    # Test that we can get string values from enum
    assert RepoType.DATASET.value == "dataset"
    assert RepoType.MODEL.value == "model"
    assert RepoType.SPACE.value == "space"
    assert RepoType.PAPER.value == "paper"


def test_parameterized_hf_mapping():
    """Test that HfMapping can be used with direct parameterization."""
    from hf.base import RepoType, HfMapping

    # Test with enum values
    dataset_mapping = HfMapping(RepoType.DATASET)
    assert dataset_mapping.repo_type == "dataset"

    model_mapping = HfMapping(RepoType.MODEL)
    assert model_mapping.repo_type == "model"

    # Test with string values (should work due to str, Enum)
    space_mapping = HfMapping("space")
    assert space_mapping.repo_type == "space"

    paper_mapping = HfMapping("paper")
    assert paper_mapping.repo_type == "paper"

    # Test that parameterized mappings have the correct functions
    for mapping in [dataset_mapping, model_mapping, space_mapping, paper_mapping]:
        assert hasattr(mapping, "loader_func")
        assert hasattr(mapping, "search_func")
        assert mapping.loader_func is not None
        assert mapping.search_func is not None
