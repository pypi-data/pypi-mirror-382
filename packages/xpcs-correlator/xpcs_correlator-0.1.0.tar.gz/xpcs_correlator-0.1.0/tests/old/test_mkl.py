import numpy as np
from xpcscorr.benchmark.utils.mkl import cblas_gemm_s8u8s32_wrapper, cblas_sgemm_wrapper, cblas_gemm_s16s16s32_wrapper

def test_cblas_gemm_s8u8s32_wrapper_basic():
    m, n, k = 2, 3, 4
    A = np.array([[1, 2, 3, 4],
                  [5, 6, 7, 8]], dtype=np.int8, order='C')
    B = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9],
                  [10, 11, 12]], dtype=np.uint8, order='C')
    C = np.zeros((m, n), dtype=np.int32, order='C')

    cblas_gemm_s8u8s32_wrapper(A, B, C, alpha=1, beta=0, ao=0, bo=0)

    # Reference result
    C_ref = np.dot(A.astype(np.int32), B.astype(np.int32))
    assert np.array_equal(C, C_ref)

def test_cblas_sgemm_wrapper_basic():
    m, n, k = 2, 3, 4
    A = np.array([[1, 2, 3, 4],
                  [5, 6, 7, 8]], dtype=np.float32, order='C')
    B = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9],
                  [10, 11, 12]], dtype=np.float32, order='C')
    C = np.zeros((m, n), dtype=np.float32, order='C')

    cblas_sgemm_wrapper(A, B, C, alpha=1.0, beta=0.0, transa='N', transb='N')

    # Reference result
    C_ref = np.dot(A, B)
    assert np.allclose(C, C_ref)  # Using allclose for floating point comparison

def test_cblas_sgemm_wrapper_transpose():
    # Test with transposition
    m, n, k = 2, 3, 4
    A = np.array([[1, 2, 3, 4],
                  [5, 6, 7, 8]], dtype=np.float32, order='C')  # 2x4
    B_t = np.array([[1, 4, 7, 10],
                    [2, 5, 8, 11],
                    [3, 6, 9, 12]], dtype=np.float32, order='C')  # 3x4
    C = np.zeros((m, n), dtype=np.float32, order='C')  # 2x3

    cblas_sgemm_wrapper(A, B_t, C, alpha=1.0, beta=0.0, transa='N', transb='T')

    # Reference result using NumPy's dot with transpose
    C_ref = np.dot(A, B_t.T)
    assert np.allclose(C, C_ref)


def test_cblas_gemm_s16s16s32_wrapper_basic():
    m, n, k = 2, 3, 4
    A = np.array([[1, 2, 3, 4],
                    [5, 6, 7, 8]], dtype=np.int16, order='C')
    B = np.array([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9],
                    [10, 11, 12]], dtype=np.int16, order='C')
    C = np.zeros((m, n), dtype=np.int32, order='C')

    cblas_gemm_s16s16s32_wrapper(A, B, C, alpha=1, beta=0, ao=0, bo=0, transa='N', transb='N')

    # Reference result
    C_ref = np.dot(A.astype(np.int32), B.astype(np.int32))
    assert np.array_equal(C, C_ref)

def test_cblas_gemm_s16s16s32_wrapper_transpose():
    m, n, k = 2, 3, 4
    A = np.array([[1, 2, 3, 4],
                  [5, 6, 7, 8]], dtype=np.int16, order='C')  # 2x4
    B_t = np.array([[1, 4, 7, 10],
                    [2, 5, 8, 11],
                    [3, 6, 9, 12]], dtype=np.int16, order='C')  # 3x4
    C = np.zeros((m, n), dtype=np.int32, order='C')  # 2x3

    cblas_gemm_s16s16s32_wrapper(A, B_t, C, alpha=1, beta=0, ao=0, bo=0, transa='N', transb='T')

    # Reference result using NumPy's dot with transpose
    C_ref = np.dot(A.astype(np.int32), B_t.T.astype(np.int32))
    assert np.array_equal(C, C_ref)