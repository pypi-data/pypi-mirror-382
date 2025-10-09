import ctypes
import numpy as np
from numpy.ctypeslib import ndpointer

# Load the oneMKL shared library
mkl = ctypes.cdll.LoadLibrary("libmkl_rt.so")

# CBLAS enums
CBLAS_LAYOUT = ctypes.c_int
CBLAS_TRANSPOSE = ctypes.c_int
CBLAS_OFFSET = ctypes.c_int  # Missing in your original code

# CBLAS layout values
CBLAS_ROW_MAJOR = 101
CBLAS_COL_MAJOR = 102

# CBLAS transpose values
CBLAS_NO_TRANS = 111
CBLAS_TRANS = 112
CBLAS_CONJ_TRANS = 113

# Correct values according to Intel MKL documentation
CBLAS_OFFSET_ROW = 171      # Use row offset vector (R)
CBLAS_OFFSET_COLUMN = 172   # Use column offset vector (C)
CBLAS_OFFSET_FIXZERO = 173  # Use fixed zero offset (F)

# Define correct argument types to match the header file
mkl.cblas_gemm_s8u8s32.argtypes = [
    CBLAS_LAYOUT,        # Layout
    CBLAS_TRANSPOSE,     # TransA
    CBLAS_TRANSPOSE,     # TransB
    CBLAS_OFFSET,        # OffsetC  <-- This was missing/wrong in your code
    ctypes.c_int,        # M
    ctypes.c_int,        # N
    ctypes.c_int,        # K
    ctypes.c_float,      # alpha (should be float, not int!)
    ctypes.c_void_p,     # A (using void* as in header)
    ctypes.c_int,        # lda
    ctypes.c_int8,       # ao
    ctypes.c_void_p,     # B (using void* as in header)
    ctypes.c_int,        # ldb
    ctypes.c_int8,       # bo
    ctypes.c_float,      # beta (should be float, not int!)
    ctypes.c_void_p,     # C
    ctypes.c_int,        # ldc
    ctypes.c_void_p      # cb (pointer to offset vector)
]
mkl.cblas_gemm_s8u8s32.restype = None

def cblas_gemm_s8u8s32_wrapper(A, B, C, alpha=1.0, beta=0.0, ao=0, bo=0):
    """
    Wrapper for cblas_gemm_s8u8s32 using row-major numpy arrays.
    A: int8 np.ndarray (m x k)
    B: uint8 np.ndarray (k x n)
    C: int32 np.ndarray (m x n)
    """
    assert A.dtype == np.int8 and A.flags['C_CONTIGUOUS']
    assert B.dtype == np.uint8 and B.flags['C_CONTIGUOUS']
    assert C.dtype == np.int32 and C.flags['C_CONTIGUOUS']

    m, k1 = A.shape
    k2, n = B.shape
    assert k1 == k2
    k = k1

    lda = k
    ldb = n
    ldc = n

    # Create a zero offset vector (just use one value for fixed offset)
    co = np.array([0], dtype=np.int32)

    # Call the MKL function with the correct parameter order
    mkl.cblas_gemm_s8u8s32(
        CBLAS_ROW_MAJOR,
        CBLAS_NO_TRANS,
        CBLAS_NO_TRANS,
        CBLAS_OFFSET_FIXZERO,  # OffsetC parameter (this was missing)
        m, n, k,
        ctypes.c_float(alpha),  # Pass alpha as float
        A.ctypes.data_as(ctypes.c_void_p),
        lda,
        ctypes.c_int8(ao),
        B.ctypes.data_as(ctypes.c_void_p),
        ldb,
        ctypes.c_int8(bo),
        ctypes.c_float(beta),  # Pass beta as float
        C.ctypes.data_as(ctypes.c_void_p),
        ldc,
        co.ctypes.data_as(ctypes.c_void_p)
    )
    return C

# Add this after your existing cblas_gemm_s8u8s32_wrapper function

# Define argtypes for cblas_sgemm
mkl.cblas_sgemm.argtypes = [
    CBLAS_LAYOUT,      # Layout
    CBLAS_TRANSPOSE,   # TransA
    CBLAS_TRANSPOSE,   # TransB
    ctypes.c_int,      # M
    ctypes.c_int,      # N
    ctypes.c_int,      # K
    ctypes.c_float,    # alpha
    ctypes.c_void_p,   # A
    ctypes.c_int,      # lda
    ctypes.c_void_p,   # B
    ctypes.c_int,      # ldb
    ctypes.c_float,    # beta
    ctypes.c_void_p,   # C
    ctypes.c_int       # ldc
]
mkl.cblas_sgemm.restype = None

def cblas_sgemm_wrapper(A, B, C, alpha=1.0, beta=0.0, transa='N', transb='N'):
    """
    Wrapper for cblas_sgemm using row-major numpy arrays.
    A: float32 np.ndarray
    B: float32 np.ndarray
    C: float32 np.ndarray
    transa: 'N' for normal, 'T' for transpose
    transb: 'N' for normal, 'T' for transpose
    """
    assert A.dtype == np.float32 and A.flags['C_CONTIGUOUS']
    assert B.dtype == np.float32 and B.flags['C_CONTIGUOUS']
    assert C.dtype == np.float32 and C.flags['C_CONTIGUOUS']
    
    # Map transpose options to CBLAS enum values
    trans_map = {'N': CBLAS_NO_TRANS, 'T': CBLAS_TRANS, 'C': CBLAS_CONJ_TRANS}
    transa_enum = trans_map.get(transa.upper(), CBLAS_NO_TRANS)
    transb_enum = trans_map.get(transb.upper(), CBLAS_NO_TRANS)
    
    # Get dimensions based on transpose settings
    if transa.upper() == 'N':
        m, k1 = A.shape
    else:
        k1, m = A.shape
        
    if transb.upper() == 'N':
        k2, n = B.shape
    else:
        n, k2 = B.shape
        
    assert k1 == k2, f"Inner dimensions must match: {k1} != {k2}"
    k = k1
    
    # Leading dimensions
    lda = A.strides[0] // A.itemsize
    ldb = B.strides[0] // B.itemsize
    ldc = C.strides[0] // C.itemsize
    
    # Call the MKL function
    mkl.cblas_sgemm(
        CBLAS_ROW_MAJOR,
        transa_enum,
        transb_enum,
        m, n, k,
        ctypes.c_float(alpha),
        A.ctypes.data_as(ctypes.c_void_p),
        lda,
        B.ctypes.data_as(ctypes.c_void_p),
        ldb,
        ctypes.c_float(beta),
        C.ctypes.data_as(ctypes.c_void_p),
        ldc
    )
    
    return C

# Define argtypes for cblas_gemm_s16s16s32
mkl.cblas_gemm_s16s16s32.argtypes = [
    CBLAS_LAYOUT,        # Layout
    CBLAS_TRANSPOSE,     # TransA
    CBLAS_TRANSPOSE,     # TransB
    CBLAS_OFFSET,        # OffsetC
    ctypes.c_int,        # M
    ctypes.c_int,        # N
    ctypes.c_int,        # K
    ctypes.c_float,      # alpha
    ctypes.c_void_p,     # A
    ctypes.c_int,        # lda
    ctypes.c_int16,      # ao
    ctypes.c_void_p,     # B
    ctypes.c_int,        # ldb
    ctypes.c_int16,      # bo
    ctypes.c_float,      # beta
    ctypes.c_void_p,     # C
    ctypes.c_int,        # ldc
    ctypes.c_void_p      # co
]
mkl.cblas_gemm_s16s16s32.restype = None

def cblas_gemm_s16s16s32_wrapper(A, B, C, alpha=1.0, beta=0.0, ao=0, bo=0, transa='N', transb='N'):
    """
    Wrapper for cblas_gemm_s16s16s32 using row-major numpy arrays.
    A: int16 np.ndarray (m x k) or (k x m) if transposed
    B: int16 np.ndarray (k x n) or (n x k) if transposed
    C: int32 np.ndarray (m x n)
    transa: 'N' for normal, 'T' for transpose
    transb: 'N' for normal, 'T' for transpose
    """
    assert A.dtype == np.int16 and A.flags['C_CONTIGUOUS']
    assert B.dtype == np.int16 and B.flags['C_CONTIGUOUS']
    assert C.dtype == np.int32 and C.flags['C_CONTIGUOUS']

    # Map transpose options to CBLAS enum values
    trans_map = {'N': CBLAS_NO_TRANS, 'T': CBLAS_TRANS, 'C': CBLAS_CONJ_TRANS}
    transa_enum = trans_map.get(transa.upper(), CBLAS_NO_TRANS)
    transb_enum = trans_map.get(transb.upper(), CBLAS_NO_TRANS)
    
    # Get dimensions based on transpose settings
    if transa.upper() == 'N':
        m, k1 = A.shape
    else:
        k1, m = A.shape
        
    if transb.upper() == 'N':
        k2, n = B.shape
    else:
        n, k2 = B.shape
        
    assert k1 == k2, f"Inner dimensions must match: {k1} != {k2}"
    k = k1

    # Leading dimensions
    lda = A.strides[0] // A.itemsize
    ldb = B.strides[0] // B.itemsize
    ldc = C.strides[0] // C.itemsize

    # Create a zero offset vector
    co = np.array([0], dtype=np.int32)

    # Call the MKL function
    mkl.cblas_gemm_s16s16s32(
        CBLAS_ROW_MAJOR,
        transa_enum,
        transb_enum,
        CBLAS_OFFSET_FIXZERO,
        m, n, k,
        ctypes.c_float(alpha),
        A.ctypes.data_as(ctypes.c_void_p),
        lda,
        ctypes.c_int16(ao),
        B.ctypes.data_as(ctypes.c_void_p),
        ldb,
        ctypes.c_int16(bo),
        ctypes.c_float(beta),
        C.ctypes.data_as(ctypes.c_void_p),
        ldc,
        co.ctypes.data_as(ctypes.c_void_p)
    )
    return C