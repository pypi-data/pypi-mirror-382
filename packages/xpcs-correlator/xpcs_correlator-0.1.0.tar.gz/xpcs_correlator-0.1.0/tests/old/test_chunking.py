import numpy as np
import pytest
from xpcscorr.benchmark.chunking.chunking import pseudo_syrk_in_chunks

def test_pseudo_syrk_in_chunks_basic():
    N_chunks = 7
    A = np.random.randint(0, 20, size=(2000, 5000), dtype=np.uint8)
    result = pseudo_syrk_in_chunks(A, N_chunks)
    A_float = A.astype(np.float64, order='C')
    result_ref = np.triu(A_float @ A_float.T)
    assert result.shape == result_ref.shape
    assert np.allclose(result, result_ref), "Chunked result does not match reference result"