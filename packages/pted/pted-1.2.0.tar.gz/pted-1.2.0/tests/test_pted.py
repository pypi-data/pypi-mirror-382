import pted

try:
    import torch
except ImportError:
    torch = None
import numpy as np

import pytest


def test_inputs_extra_dims():
    np.random.seed(42)
    # Test with numpy arrays
    x = np.random.normal(size=(100, 30, 30))
    y = np.random.normal(size=(100, 30, 30))
    p = pted.pted(x, y)
    assert p > 1e-2 and p < 0.99, f"p-value {p} is not in the expected range (U(0,1))"

    if torch is None:
        pytest.skip("torch not installed")
    # Test with torch tensors
    g = torch.randn(100, 30, 30)
    s = torch.randn(50, 100, 30, 30)
    p = pted.pted_coverage_test(g, s)
    assert p > 1e-2 and p < 0.99, f"p-value {p} is not in the expected range (U(0,1))"


def test_pted_main():
    pted.test()


def test_pted_torch():
    if torch is None:
        pytest.skip("torch not installed")

    # Set the random seed for reproducibility
    torch.manual_seed(41)
    np.random.seed(42)

    # example 2 sample test
    D = 300
    for _ in range(20):
        x = torch.randn(100, D)
        y = torch.randn(100, D)
        p = pted.pted(x, y)
        assert p > 1e-2 and p < 0.99, f"p-value {p} is not in the expected range (U(0,1))"

    x = torch.randn(100, D)
    y = torch.rand(100, D)
    p = pted.pted(x, y, two_tailed=False)
    assert p < 1e-2, f"p-value {p} is not in the expected range (~0)"

    x = torch.randn(100, D)
    t, p = pted.pted(x, x, return_all=True)
    q = 2 * min(np.sum(p > t), np.sum(p < t))
    p = (1 + q) / (len(p) + 1)  # add one to numerator and denominator to avoid p=0
    assert p < 1e-2, f"p-value {p} is not in the expected range (~0)"


def test_pted_coverage_full():
    g = np.random.normal(size=(100, 10))  # ground truth (n_simulations, n_dimensions)
    s = np.random.normal(
        size=(200, 100, 10)
    )  # posterior samples (n_samples, n_simulations, n_dimensions)

    test, permute = pted.pted_coverage_test(g, s, permutations=100, return_all=True)
    assert test.shape == (100,)
    assert permute.shape == (100, 100)


def test_pted_chunk_torch():
    if torch is None:
        pytest.skip("torch not installed")
    np.random.seed(42)
    torch.manual_seed(42)

    # example 2 sample test
    D = 10
    x = torch.randn(1000, D)
    y = torch.randn(1000, D)
    p = pted.pted(x, y, chunk_size=100, chunk_iter=10)
    assert p > 1e-2 and p < 0.99, f"p-value {p} is not in the expected range (U(0,1))"

    y = torch.rand(1000, D)
    p = pted.pted(x, y, chunk_size=100, chunk_iter=10)
    assert p < 1e-2, f"p-value {p} is not in the expected range (~0)"


def test_pted_chunk_numpy():
    np.random.seed(42)

    # example 2 sample test
    D = 10
    x = np.random.normal(size=(1000, D))
    y = np.random.normal(size=(1000, D))
    p = pted.pted(x, y, chunk_size=100, chunk_iter=10)
    assert p > 1e-2 and p < 0.99, f"p-value {p} is not in the expected range (U(0,1))"

    y = np.random.uniform(size=(1000, D))
    p = pted.pted(x, y, chunk_size=100, chunk_iter=10)
    assert p < 1e-2, f"p-value {p} is not in the expected range (~0)"


def test_pted_coverage_edgecase():
    # Test with single simulation
    g = np.random.normal(size=(1, 10))
    s = np.random.normal(size=(100, 1, 10))
    p = pted.pted_coverage_test(g, s)
    assert p > 1e-2 and p < 0.99, f"p-value {p} is not in the expected range (U(0,1))"


def test_pted_coverage_overunder():
    if torch is None:
        pytest.skip("torch not installed")
    g = torch.randn(100, 3)
    s = torch.randn(50, 100, 3)
    with pytest.warns(pted.utils.OverconfidenceWarning):
        pted.pted_coverage_test(g, s * 0.5)
    with pytest.warns(pted.utils.UnderconfidenceWarning):
        pted.pted_coverage_test(g, s * 2)
