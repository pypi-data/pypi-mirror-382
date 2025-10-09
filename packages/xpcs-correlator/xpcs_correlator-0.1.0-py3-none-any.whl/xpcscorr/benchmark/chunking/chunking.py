from multiprocessing.connection import Client
import numpy as np
from scipy.linalg.blas import dsyrk as dsyrk_blas  # type: ignore
from scipy.linalg.blas import ssyrk as ssyrk_blas  # type: ignore
from time import time

import logging
logger = logging.getLogger(__name__)

#float32:
#2^24 = 16,777,216 = 1.6777216e+07

#float64:
#2^53 = 9,007,199,254,740,992 = 9.007199254740992e+15

#int32:
#2^31 - 1 = 2,147,483,647 = 2.147483647e+09

#int64:
#2^63 - 1 = 9,223,372,036,854,775,807 = 9.223372036854776e+18

def upper_triangle_snake(N):
    """
    Generate a zig-zag path for the upper triangle of an NxN matrix:
    - Start at (0,0), move right to (0,N-1)
    - Drop to (1,N-1), move left to (1,1)
    - Drop diagonally to (2,2), move right to (2,N-1)
    - Continue this pattern...
    Returns a list of (i, j) tuples (0-based indexing).
    """
    path = []
    i, j = 0, 0
    direction = 'right'
    while i < N and j < N:
        if i <= j:
            path.append((i, j))
        if direction == 'right':
            if j < N - 1:
                j += 1
            else:
                i += 1
                direction = 'left'
        elif direction == 'left':
            if j > i:
                j -= 1
            else:
                i += 1
                direction = 'right'
    return path

def num_upper_triangle_steps(N):
    """
    Returns the number of steps in the upper triangle (including diagonal) of an NxN matrix.
    Formula: N * (N + 1) // 2
    """
    return N * (N + 1) // 2

def animate_upper_triangle_snake(N, delay=0.3):
    """
    Animate the custom zig-zag path in the terminal.
    """
    import os
    import time
    path = upper_triangle_snake(N)
    path_elements = num_upper_triangle_steps(N)
    matrix = [['.' for _ in range(N)] for _ in range(N)]

    for step, (i, j) in enumerate(path):
        os.system('clear')
        display = [row[:] for row in matrix]
        display[i][j] = 'X'
        print(f"Step {step+1}/{path_elements}: (i={i}, j={j})")
        for row in display:
            print(' '.join(row))
        print('-' * (2*N))
        time.sleep(delay)

def get_chunk_indices(matrix_size, num_chunks, chunk_indices):
    """
    Calculate the row and column indices for a chunk in an NxN grid.

    Args:
        matrix_size (int): Size of the square matrix (NxN).
        num_chunks (int): Number of chunks per dimension.
        chunk_indices (tuple): Tuple of (row_idx, col_idx) for the chunk (0-based).

    Returns:
        (row_start, row_end, col_start, col_end): Indices for the chunk.
    """
    chunk_row, chunk_col = chunk_indices
    chunk_height = matrix_size // num_chunks
    chunk_width = matrix_size // num_chunks

    row_start = chunk_row * chunk_height
    row_end = (chunk_row + 1) * chunk_height - 1
    col_start = chunk_col * chunk_width
    col_end = (chunk_col + 1) * chunk_width - 1

    # Handle remainder if matrix_size is not divisible by num_chunks
    if chunk_row == num_chunks - 1:
        row_end = matrix_size - 1
    if chunk_col == num_chunks - 1:
        col_end = matrix_size - 1

    return row_start, row_end, col_start, col_end

def get_chunks_info(matrix_size, num_chunks):
    """
    Get information about the chunks in an NxN matrix.

    Args:
        matrix_size (int): Size of the square matrix (NxN).
        num_chunks (int): Number of chunks per dimension.

    Returns:
        dict: Dictionary where key is chunk number, value is dict with indices, sizes, and total elements.
    """
    chunks_info = {}

    for chunk_num,n in enumerate(upper_triangle_snake(num_chunks)):
        i,j=n
        row_start, row_end, col_start, col_end = get_chunk_indices(matrix_size, num_chunks, (i, j))
        row_size = row_end - row_start + 1
        col_size = col_end - col_start + 1
        total_elements = row_size * col_size
        chunks_info[chunk_num] = {
            "indices": {
                "row_start": row_start,
                "row_end": row_end,
                "col_start": col_start,
                "col_end": col_end
            },
            "row_size": row_size,
            "col_size": col_size,
            "total_elements": total_elements
        }
        chunk_num += 1
    return chunks_info

#TODO Introduce more efficient buffering it is not necessary to load chunkA and chunk B for
#each chunk, we need to load only one for each next chunk , beside diagonal.


def matmul_tiled_any_to_float64(A, B, tile_width=1024):
    """
    Compute A @ B for large matrices A and B using column-wise tiling.
    Each tile is upcast to float32 for safe multiplication, and accumulated into float64 output.

    Args:
        A (np.ndarray): Input matrix of shape (N, M), any dtype.
        B (np.ndarray): Input matrix of shape (M, K), any dtype.
        tile_width (int): Number of columns per tile.

    Returns:
        np.ndarray: Output matrix of shape (N, K), dtype=float64.
    """
    N, M = A.shape
    M2, K = B.shape
    assert M == M2, "Inner dimensions must match for matrix multiplication."
    assert A.dtype == B.dtype, "Input matrices must have the same dtype."
    output = np.zeros((N, K), dtype=np.float64)

    for col_start in range(0, M, tile_width):
        col_end = min(col_start + tile_width, M)
        # Upcast tiles to float32 for safe multiplication
        A_tile = A[:, col_start:col_end].astype(np.float32, copy=False)      # (N, tile)
        B_tile = B[col_start:col_end, :].astype(np.float32, copy=False)      # (tile, K)
        partial = A_tile @ B_tile                                            # (N, K), float32
        output += partial.astype(np.float64, copy=False)

    return output

import cupy as cp

def matmul_tiled_any_to_float64_cupy(A, B, tile_width=1024):
    """
    Compute A @ B for large matrices A and B using column-wise tiling on GPU (CuPy).
    Each tile is upcast to float32 for safe multiplication, and accumulated into float64 output.

    Args:
        A (np.ndarray or cp.ndarray): Input matrix of shape (N, M), any dtype.
        B (np.ndarray or cp.ndarray): Input matrix of shape (M, K), any dtype.
        tile_width (int): Number of columns per tile.

    Returns:
        cp.ndarray: Output matrix of shape (N, K), dtype=float64 (on GPU).
    """
    # Convert input to cupy arrays if not already
    A_gpu = cp.asarray(A)
    B_gpu = cp.asarray(B)
    N, M = A_gpu.shape
    M2, K = B_gpu.shape
    assert M == M2, "Inner dimensions must match for matrix multiplication."
    output = cp.zeros((N, K), dtype=cp.float64)

    for col_start in range(0, M, tile_width):
        col_end = min(col_start + tile_width, M)
        # Upcast tiles to float32 for safe multiplication
        A_tile = A_gpu[:, col_start:col_end].astype(cp.float32, copy=False)
        B_tile = B_gpu[col_start:col_end, :].astype(cp.float32, copy=False)
        partial = A_tile @ B_tile  # (N, K), float32
        output += partial.astype(cp.float64, copy=False)

    return output

#General conclusion is that blas method working on int is slower than float
def matmul_tiled_int16_to_float64(A, B, tile_width=1024):
    """
    Compute A @ B for large int16 matrices using column-wise tiling and MKL's cblas_gemm_s16s16s32.
    Each tile is multiplied in int32 and accumulated into float64 output.

    Args:
        A (np.ndarray): Input matrix of shape (N, M), dtype=int16.
        B (np.ndarray): Input matrix of shape (M, K), dtype=int16.
        tile_width (int): Number of columns per tile.

    Returns:
        np.ndarray: Output matrix of shape (N, K), dtype=float64.
    """
    from xpcscorr.benchmark.utils.mkl import cblas_gemm_s16s16s32_wrapper

    N, M = A.shape
    M2, K = B.shape
    assert M == M2, "Inner dimensions must match for matrix multiplication."
    
    output = np.zeros((N, K), dtype=np.float64)
    C_tile = np.zeros((N, K), dtype=np.int32)  # Temporary tile for int32 accumulation

    for col_start in range(0, M, tile_width):
        col_end = min(col_start + tile_width, M)
        # Extract tiles and ensure int16 dtype and C-contiguous
        A_tile = np.ascontiguousarray(A[:, col_start:col_end], dtype=np.int16)  # (N, tile)
        B_tile = np.ascontiguousarray(B[col_start:col_end, :], dtype=np.int16)  # (tile, K)
        # Allocate C_tile for int32 result
        
        # Perform multiplication using MKL wrapper
        cblas_gemm_s16s16s32_wrapper(A_tile, B_tile, C_tile, alpha=1.0, beta=1.0, transa='N', transb='N')
        
        # Accumulate result into output as float64
        output += C_tile.astype(np.float64, copy=False)
        C_tile.fill(0)  # Reset C_tile for next accumulation
    return output



def pseudo_syrk_in_chunks(matrix, num_chunks):
    """
    Calculate upper triangle of A @ A^T in chunks
    
    Args:
        matrix (np.array): The input matrix.
        num_chunks (int): Number of chunks per dimension.
    
    Returns:
        np.array: Resulting upper triangle matrix.
    """
    logger.info(f"Starting pseudo_syrk_in_chunks for matrix shape {matrix.shape} with {num_chunks} chunks")

    output= np.empty((matrix.shape[0], matrix.shape[0]))
    chunk_info = get_chunks_info(matrix.shape[0], num_chunks)

    #here we are finding maximum cunk size in rows and columns
    max_row_size = max(info['row_size'] for info in chunk_info.values())
    max_col_size = max(info['col_size'] for info in chunk_info.values())

    buffer_a=np.empty((max_row_size,matrix.shape[1]), dtype=np.float64)
    buffer_b=np.empty((matrix.shape[1],max_col_size), dtype=np.float64)

    for n_chunk,n in enumerate(upper_triangle_snake(num_chunks)):
        start_time = time()
        logger.info(f"Processing chunk {n_chunk} of {len(upper_triangle_snake(num_chunks))} total chunks")
        
        i, j = n
        row_start, row_end, col_start, col_end = get_chunk_indices(matrix.shape[0], num_chunks, (i, j))
        
        buffer_a[0:chunk_info[n_chunk]['row_size']] = \
            matrix[row_start:row_end+1, :].astype(np.float64, order='C')
    
        A_chunk = buffer_a[0:chunk_info[n_chunk]['row_size']]
        
        # Ensure the chunk is in float32 or float64 format
        if A_chunk.dtype not in [np.float32, np.float64]:
            raise ValueError("Unsupported matrix dtype. Use float32 or float64.")

        logger.info(f"Chunk {n} number of rows  {row_end-row_start+1}, dtype: {A_chunk.dtype}")
        if i== j:
            # Use dsyrk for the diagonal chunk
            if A_chunk.dtype == np.float32:
                output[row_start:row_end+1, row_start:row_end+1] = ssyrk_blas(alpha=1.0, a=A_chunk, lower=0, trans=0)
            elif A_chunk.dtype == np.float64:
                output[row_start:row_end+1, row_start:row_end+1] = dsyrk_blas(alpha=1.0, a=A_chunk, lower=0, trans=0)   
        else:
            buffer_b[:,0:chunk_info[n_chunk]['col_size']] = \
                matrix[col_start:col_end+1, :].T.astype(np.float64, order='C')
            
            B_chunk = buffer_b[:,0:chunk_info[n_chunk]['col_size']]
            output[row_start:row_end+1, col_start:col_end+1] = np.dot(A_chunk, B_chunk)

        logger.info(f"Chunk {n} processed in {time() - start_time:.2f} seconds")

    return output

#Optimized version of v1
def pseudo_syrk_in_chunks2(matrix, num_chunks):
    """
    Calculate upper triangle of A @ A^T in chunks. It operates only on the chunks which are
    float64 to prevent any possible overflows.

    Args:
        matrix (np.array): The input matrix (int8 in your case).
        num_chunks (int): Number of chunks per dimension.

    Returns:
        np.array: Resulting upper triangle matrix.
    """
  

    N = matrix.shape[0]
    output = np.zeros((N, N), dtype=np.float64)

    chunk_info = get_chunks_info(N, num_chunks)
    path = list(upper_triangle_snake(num_chunks))
    max_row_size = max(info["row_size"] for info in chunk_info.values())
    max_col_size = max(info["col_size"] for info in chunk_info.values())
    ncols = matrix.shape[1]

    logger.info(
        f"Starting pseudo_syrk_in_chunks2 for matrix shape {matrix.shape} "
        f"with {num_chunks} frame chunks and total chunks {len(path)}"
    )

    # preallocate reusable buffers (float64)
    buffer_a = np.empty((max_row_size, ncols), dtype=np.float64, order="C")
    buffer_b = np.empty((max_col_size, ncols), dtype=np.float64, order="C")

    i_prev = j_prev = None

    for n_chunk, (i, j) in enumerate(path):
        t0 = time()
        info = chunk_info[n_chunk]
        rs = info["indices"]["row_start"]
        re = info["indices"]["row_end"]
        cs = info["indices"]["col_start"]
        ce = info["indices"]["col_end"]
        row_size = info["row_size"]
        col_size = info["col_size"]

        logger.info(f"Processing chunk {n_chunk} ({i}, {j}) of {len(path)} total chunks")

        # load A chunk only when row index changed
        if i_prev is None or i != i_prev:
            np.copyto(
                buffer_a[:row_size, :],
                matrix[rs : re + 1, :].astype(np.float64, order="C"),
            )
        A_chunk = buffer_a[:row_size, :]

        # load B chunk only when col index changed
        if j_prev is None or j != j_prev and i != j:
            np.copyto(
                buffer_b[:col_size, :],
                matrix[cs : ce + 1, :].astype(np.float64, order="C"),
            )
        B_chunk = buffer_b[:col_size, :]

        # compute block (row_size x col_size)
        if i == j:
             # for diagonal blocks keep only upper-triangular part
            #block= dsyrk_blas(alpha=1.0, a=A_chunk, lower=0, trans=0)
            block = A_chunk @ A_chunk.T
            block = np.triu(block)
        else:
            block = A_chunk @ B_chunk.T

        output[rs : re + 1, cs : ce + 1] = block

        i_prev, j_prev = i, j
        logger.info(
            f"Chunk processed in {time() - t0:.2f} seconds, "
            f"row_size={row_size}, col_size={col_size}"
        )

    return output

# Optimized version of v2 , using tiling to calculate chunks
def pseudo_syrk_in_chunks3(matrix, num_chunks, tile_width=1024):
    """
    Calculate upper triangle of A @ A^T in chunks. It operates only on the chunks which are
    float64 to prevent any possible overflows. The chunks are calulated using tiles and upcasting
    float32 as input to float64 as an output.

    Args:
        matrix (np.array): The input matrix (int8 in your case).
        num_chunks (int): Number of chunks per dimension.

    Returns:
        np.array: Resulting upper triangle matrix.
    """
  

    N = matrix.shape[0]
    output = np.zeros((N, N), dtype=np.float64)

    chunk_info = get_chunks_info(N, num_chunks)
    path = list(upper_triangle_snake(num_chunks))
    max_row_size = max(info["row_size"] for info in chunk_info.values())
    max_col_size = max(info["col_size"] for info in chunk_info.values())
    ncols = matrix.shape[1]

    logger.info(
        f"Starting pseudo_syrk_in_chunks3 for matrix shape {matrix.shape} "
        f"with {num_chunks} frame chunks and total chunks {len(path)}"
    )

    # preallocate reusable buffers (float64)
    logger.info(f"Preallocating buffers of size {max_row_size} x {ncols} and {max_col_size} x {ncols}")
    buffer_a = np.empty((max_row_size, ncols), dtype=np.float32, order="C")
    buffer_b = np.empty((max_col_size, ncols), dtype=np.float32, order="C")

    i_prev = j_prev = None

    for n_chunk, (i, j) in enumerate(path):
        t0 = time()
        info = chunk_info[n_chunk]
        rs = info["indices"]["row_start"]
        re = info["indices"]["row_end"]
        cs = info["indices"]["col_start"]
        ce = info["indices"]["col_end"]
        row_size = info["row_size"]
        col_size = info["col_size"]

        logger.info(f"Processing chunk {n_chunk} ({i}, {j}) of {len(path)} total chunks")

        # load A chunk only when row index changed
        if i_prev is None or i != i_prev:
            logger.info(f"Loading A chunk for rows {rs} to {re}")
            
            #TODO this copyto takes a lot of ram due to the type conversion
            np.copyto(
                buffer_a[:row_size, :],
                matrix[rs : re + 1, :].astype(np.float32, order="C"),
            )
            
        A_chunk = buffer_a[:row_size, :]

        # load B chunk only when col index changed
        if (j_prev is None or j != j_prev) and i != j:
            logger.info(f"Loading B chunk for cols {cs} to {ce}")
            np.copyto(
                buffer_b[:col_size, :],
                matrix[cs : ce + 1, :].astype(np.float32, order="C"),
            )
        B_chunk = buffer_b[:col_size, :]

        # compute block (row_size x col_size)
        if i == j:
             # for diagonal blocks keep only upper-triangular part
            #block= dsyrk_blas(alpha=1.0, a=A_chunk, lower=0, trans=0)
            logger.info("Copying A_chunk to B_chunk")
            np.copyto(B_chunk, A_chunk)
            logger.info("Calculating block with tiling")
            block = matmul_tiled_any_to_float64(A_chunk, B_chunk.T, tile_width=tile_width)
            block = np.triu(block)
        else:
            block = matmul_tiled_any_to_float64(A_chunk, B_chunk.T, tile_width=tile_width)

        output[rs : re + 1, cs : ce + 1] = block

        i_prev, j_prev = i, j
        logger.info(
            f"Chunk processed in {time() - t0:.2f} seconds, "
            f"row_size={row_size}, col_size={col_size}"
        )

    return output

#This works but when pixel values are maximum 4096 above use v3 OR v3c
def pseudo_syrk_in_chunks3b(matrix, num_chunks, tile_width=1024):
    """
    Calculate upper triangle of A @ A^T in chunks. It operates only on the chunks which are
    float32 to prevent any possible overflows and speed.The chunks are calulated using standard
    numpy matmul and the output is float32 as well.

    Args:
        matrix (np.array): The input matrix (int8 in your case).
        num_chunks (int): Number of chunks per dimension.

    Returns:
        np.array: Resulting upper triangle matrix.
    """
  

    N = matrix.shape[0]
    output = np.zeros((N, N), dtype=np.float32)

    chunk_info = get_chunks_info(N, num_chunks)
    path = list(upper_triangle_snake(num_chunks))
    max_row_size = max(info["row_size"] for info in chunk_info.values())
    max_col_size = max(info["col_size"] for info in chunk_info.values())
    ncols = matrix.shape[1]

    logger.info(
        f"Starting pseudo_syrk_in_chunks3b for matrix shape {matrix.shape} "
        f"with {num_chunks} frame chunks and total chunks {len(path)}"
    )

    # preallocate reusable buffers (float64)
    logger.info(f"Preallocating buffers of size {max_row_size} x {ncols} and {max_col_size} x {ncols}")
    buffer_a = np.empty((max_row_size, ncols), dtype=np.float32, order="C")
    buffer_b = np.empty((max_col_size, ncols), dtype=np.float32, order="C")

    i_prev = j_prev = None

    for n_chunk, (i, j) in enumerate(path):
        t0 = time()
        info = chunk_info[n_chunk]
        rs = info["indices"]["row_start"]
        re = info["indices"]["row_end"]
        cs = info["indices"]["col_start"]
        ce = info["indices"]["col_end"]
        row_size = info["row_size"]
        col_size = info["col_size"]

        logger.info(f"Processing chunk {n_chunk} ({i}, {j}) of {len(path)} total chunks")

        # load A chunk only when row index changed
        if i_prev is None or i != i_prev:
            logger.info(f"Loading A chunk for rows {rs} to {re}")
            
            #TODO this copyto takes a lot of ram due to the type conversion
            np.copyto(
                buffer_a[:row_size, :],
                matrix[rs : re + 1, :].astype(np.float32, order="C"),
            )
            
        A_chunk = buffer_a[:row_size, :]

        # load B chunk only when col index changed
        if (j_prev is None or j != j_prev) and i != j:
            logger.info(f"Loading B chunk for cols {cs} to {ce}")
            np.copyto(
                buffer_b[:col_size, :],
                matrix[cs : ce + 1, :].astype(np.float32, order="C"),
            )
        B_chunk = buffer_b[:col_size, :]

        # compute block (row_size x col_size)
        if i == j:
             # for diagonal blocks keep only upper-triangular part
            #block= dsyrk_blas(alpha=1.0, a=A_chunk, lower=0, trans=0)
            logger.info("Copying A_chunk to B_chunk")
            np.copyto(B_chunk, A_chunk)
            logger.info("Calculating block using native numpy matmul")
            block = np.matmul(A_chunk, B_chunk.T)
            block = np.triu(block)
        else:
            logger.info("Calculating block using native numpy matmul")
            block = np.matmul(A_chunk, B_chunk.T)

        output[rs : re + 1, cs : ce + 1] = block

        i_prev, j_prev = i, j
        logger.info(
            f"Chunk processed in {time() - t0:.2f} seconds, "
            f"row_size={row_size}, col_size={col_size}"
        )

    return output


#This works where everything is upcasted to float64bit- exopensive memory
def pseudo_syrk_in_chunks3c(matrix, num_chunks, dtype_upcast=np.float32, tile_width=1024):
    """
    Calculate upper triangle of A @ A^T in chunks. It operates only on the chunks which are
    float64 or float32 to prevent any possible overflows and speed.The chunks are calulated using standard
    numpy matmul and the output is float32 or float64 as well.

    Args:
        matrix (np.array): The input matrix (int8 in your case).
        num_chunks (int): Number of chunks per dimension.
        dtype_upcast (np.dtype): The dtype to upcast the chunks and output to (float32 or float64).

    Returns:
        np.array: Resulting upper triangle matrix.
    """
  

    N = matrix.shape[0]
    output = np.zeros((N, N), dtype=dtype_upcast)

    chunk_info = get_chunks_info(N, num_chunks)
    path = list(upper_triangle_snake(num_chunks))
    max_row_size = max(info["row_size"] for info in chunk_info.values())
    max_col_size = max(info["col_size"] for info in chunk_info.values())
    ncols = matrix.shape[1]

    logger.info(
        f"Starting pseudo_syrk_in_chunks3c for matrix shape {matrix.shape} "
        f"with {num_chunks} frame chunks and total chunks {len(path)}"
    )

    # preallocate reusable buffers (float64)
    logger.info(f"Preallocating buffers of size {max_row_size} x {ncols} and {max_col_size} x {ncols}")
    buffer_a = np.empty((max_row_size, ncols), dtype=dtype_upcast, order="C")
    buffer_b = np.empty((max_col_size, ncols), dtype=dtype_upcast, order="C")

    i_prev = j_prev = None

    for n_chunk, (i, j) in enumerate(path):
        t0 = time()
        info = chunk_info[n_chunk]
        rs = info["indices"]["row_start"]
        re = info["indices"]["row_end"]
        cs = info["indices"]["col_start"]
        ce = info["indices"]["col_end"]
        row_size = info["row_size"]
        col_size = info["col_size"]

        logger.info(f"Processing chunk {n_chunk} ({i}, {j}) of {len(path)} total chunks")

        # load A chunk only when row index changed
        if i_prev is None or i != i_prev:
            logger.info(f"Loading A chunk for rows {rs} to {re}")
            
            #TODO this copyto takes a lot of ram due to the type conversion
            np.copyto(
                buffer_a[:row_size, :],
                matrix[rs : re + 1, :].astype(dtype_upcast, order="C"),
            )
            
        A_chunk = buffer_a[:row_size, :]

        # load B chunk only when col index changed
        if (j_prev is None or j != j_prev) and i != j:
            logger.info(f"Loading B chunk for cols {cs} to {ce}")
            np.copyto(
                buffer_b[:col_size, :],
                matrix[cs : ce + 1, :].astype(dtype_upcast, order="C"),
            )
        B_chunk = buffer_b[:col_size, :]

        # compute block (row_size x col_size)
        if i == j:
             # for diagonal blocks keep only upper-triangular part
            #block= dsyrk_blas(alpha=1.0, a=A_chunk, lower=0, trans=0)
            logger.info("Copying A_chunk to B_chunk")
            np.copyto(B_chunk, A_chunk)
            logger.info("Calculating block using native numpy matmul")
            block = np.matmul(A_chunk, B_chunk.T)
            block = np.triu(block)
        else:
            logger.info("Calculating block using native numpy matmul")
            block = np.matmul(A_chunk, B_chunk.T)

        output[rs : re + 1, cs : ce + 1] = block

        i_prev, j_prev = i, j
        logger.info(
            f"Chunk processed in {time() - t0:.2f} seconds, "
            f"row_size={row_size}, col_size={col_size}"
        )

    return output


#Using mkl blas working on int is slower than working on float- v3
def pseudo_syrk_in_chunks4(matrix, num_chunks, tile_width=1024):
    """
    Calculate upper triangle of A @ A^T in chunks using tiled multiplication for int16 input.
    Uses matmul_tiled_int16_to_float64 for safe and efficient computation.

    Args:
        matrix (np.ndarray): The input matrix (int16).
        num_chunks (int): Number of chunks per dimension.
        tile_width (int): Number of columns per tile for matmul_tiled_int16_to_float64.

    Returns:
        np.ndarray: Resulting upper triangle matrix (float64).
    """
    N = matrix.shape[0]
    output = np.zeros((N, N), dtype=np.float64)

    chunk_info = get_chunks_info(N, num_chunks)
    path = list(upper_triangle_snake(num_chunks))
    max_row_size = max(info["row_size"] for info in chunk_info.values())
    max_col_size = max(info["col_size"] for info in chunk_info.values())
    ncols = matrix.shape[1]

    logger.info(
        f"Starting pseudo_syrk_in_chunks4 for matrix shape {matrix.shape} "
        f"with {num_chunks} frame chunks and total chunks {len(path)}"
    )

    # Preallocate reusable buffers (int16)
    buffer_a = np.empty((max_row_size, ncols), dtype=np.int16, order="C")
    buffer_b = np.empty((max_col_size, ncols), dtype=np.int16, order="C")

    i_prev = j_prev = None

    for n_chunk, (i, j) in enumerate(path):
        t0 = time()
        info = chunk_info[n_chunk]
        rs = info["indices"]["row_start"]
        re = info["indices"]["row_end"]
        cs = info["indices"]["col_start"]
        ce = info["indices"]["col_end"]
        row_size = info["row_size"]
        col_size = info["col_size"]

        logger.info(f"Processing chunk {n_chunk} ({i}, {j}) of {len(path)} total chunks")

        # load A chunk only when row index changed
        if i_prev is None or i != i_prev:
            np.copyto(
                buffer_a[:row_size, :],
                matrix[rs : re + 1, :],
            )
        A_chunk = buffer_a[:row_size, :]

        # load B chunk only when col index changed
        if j_prev is None or j != j_prev and i != j:
            np.copyto(
                buffer_b[:col_size, :],
                matrix[cs : ce + 1, :],
            )
        B_chunk = buffer_b[:col_size, :]

        # compute block (row_size x col_size)
        if i == j:
            np.copyto(B_chunk, A_chunk)
            block = matmul_tiled_int16_to_float64(A_chunk, B_chunk.T,tile_width=tile_width)
            block = np.triu(block)
        else:
            block = matmul_tiled_int16_to_float64(A_chunk, B_chunk.T,tile_width=tile_width)

        output[rs : re + 1, cs : ce + 1] = block

        i_prev, j_prev = i, j
        logger.info(
            f"Chunk processed in {time() - t0:.2f} seconds, "
            f"row_size={row_size}, col_size={col_size}"
        )

    return output

def pseudo_syrk_in_chunks5(matrix, num_chunks, tile_width=128*1024):
    """
    Calculate upper triangle of A @ A^T in chunks using tiled multiplication on GPU (CuPy).
    Uses matmul_tiled_any_to_float64_cupy for safe and efficient computation.

    Args:
        matrix (np.ndarray or cp.ndarray): The input matrix (any dtype).
        num_chunks (int): Number of chunks per dimension.
        tile_width (int): Number of columns per tile for matmul_tiled_any_to_float64_cupy.

    Returns:
        cp.ndarray: Resulting upper triangle matrix (float64, on GPU).
    """
    import cupy as cp

    N = matrix.shape[0]
    output = np.zeros((N, N), dtype=np.float64)

    chunk_info = get_chunks_info(N, num_chunks)
    path = list(upper_triangle_snake(num_chunks))
    max_row_size = max(info["row_size"] for info in chunk_info.values())
    max_col_size = max(info["col_size"] for info in chunk_info.values())
    ncols = matrix.shape[1]

    logger.info(
        f"Starting pseudo_syrk_in_chunks5 for matrix shape {matrix.shape} "
        f"with {num_chunks} frame chunks and total chunks {len(path)}"
    )


    # Preallocate reusable buffers (on GPU)
    buffer_a = cp.empty((max_row_size, ncols), dtype=cp.float32)
    buffer_b = cp.empty((max_col_size, ncols), dtype=cp.float32)

    i_prev = j_prev = None

    for n_chunk, (i, j) in enumerate(path):
        t0 = time()
        info = chunk_info[n_chunk]
        rs = info["indices"]["row_start"]
        re = info["indices"]["row_end"]
        cs = info["indices"]["col_start"]
        ce = info["indices"]["col_end"]
        row_size = info["row_size"]
        col_size = info["col_size"]

        logger.info(f"Processing chunk {n_chunk+1} ({i}, {j}) of {len(path)} total chunks")

        # load A chunk only when row index changed
        if i_prev is None or i != i_prev:
            buffer_a[:row_size, :] = cp.asarray(matrix[rs : re + 1, :]).astype(cp.float32)
            # More GPU memory but slower
            #buffer_a_view = buffer_a[:row_size, :]
            #buffer_a_view.set(matrix[rs : re + 1, :].astype(np.float32))
            #buffer_a_view = buffer_a_view.astype(cp.float32, copy=False)
        A_chunk = buffer_a[:row_size, :]

        # load B chunk only when col index changed
        if j_prev is None or j != j_prev and i != j:
            buffer_b[:col_size, :] = cp.asarray(matrix[cs : ce + 1, :]).astype(cp.float32)
            # More GPU memory but slower
            #buffer_b_view = buffer_b[:col_size, :]
            #buffer_b_view.set(matrix[cs : ce + 1, :].astype(np.float32))
            #buffer_b_view = buffer_b_view.astype(cp.float32, copy=False)
        B_chunk = buffer_b[:col_size, :]

        # compute block (row_size x col_size)
        if i == j:
            #TODO load A_chunk in B_chunk ??? like in v3
            block = matmul_tiled_any_to_float64_cupy(A_chunk, A_chunk.T, tile_width=tile_width)
            block = cp.triu(block)
        else:
            block = matmul_tiled_any_to_float64_cupy(A_chunk, B_chunk.T, tile_width=tile_width)

        #output[rs : re + 1, cs : ce + 1] = block.get()

        i_prev, j_prev = i, j
        logger.info(
            f"Chunk processed in {time() - t0:.2f} seconds, "
            f"row_size={row_size}, col_size={col_size}"
        )
    return output


def pseudo_syrk_in_chunks6(matrix, num_chunks, dtype_upcast="float64", local=False, chunk_size=(1000, 50_000)):
    """
    Calculate upper triangle of A @ A^T in chunks. It operates only on the chunks which are
    float64 or float32 to prevent any possible overflows and speed.The chunks are calulated using standard
    numpy matmul and the output is float32 or float64 as well.

    Args:
        matrix (np.array): The input matrix (int8 in your case).
        num_chunks (int): Number of chunks per dimension.
        dtype_upcast (np.dtype): The dtype to upcast the chunks and output to (float32 or float64).

    Returns:
        np.array: Resulting upper triangle matrix.
    """


    from dask_jobqueue.slurm import SLURMCluster 
    from dask.distributed import Client,LocalCluster
    import dask.array as da


    if local:
        cluster = LocalCluster(
        n_workers=1,         # number of worker processes
        threads_per_worker=16,# threads per worker (CPUS)
        memory_limit='200 GB', # memory per worker
        host='0.0.0.0',         
        )
        client = Client(cluster)
    else:
        cluster = SLURMCluster(
            queue="nice-long",
            cores=32,       # total cores per node
            memory="200 GB", # memory per node
            processes=4,     # n processes per node
            walltime="01:00:00",
        )
        cluster.scale(160)  # n workers = n nodes * n processes per node
        client = Client(cluster)
    print("Dask dashboard:", client.dashboard_link)

    N = matrix.shape[0]
    

    chunk_info = get_chunks_info(N, num_chunks)
    path = list(upper_triangle_snake(num_chunks))
    max_row_size = max(info["row_size"] for info in chunk_info.values())
    max_col_size = max(info["col_size"] for info in chunk_info.values())
    ncols = matrix.shape[1]

    logger.info(
        f"Starting pseudo_syrk_in_chunks6 (dask) for matrix shape {matrix.shape} "
        f"with {num_chunks} frame chunks and total chunks {len(path)}"
    )

    
    i_prev = j_prev = None

    output = np.zeros((N, N), dtype=np.float64)  # needs to be numpy array for speed
   #output = da.zeros((N, N), dtype=dtype_upcast)

    

    matrix_da = da.from_array(matrix, chunks=chunk_size)
    
    #mask=np.zeros((2000,2000), dtype=bool)
    #mask[900:1100, 900:1100] = True
    #mask=mask.flatten()
    #matrix_da= matrix_da[:, mask] 

    for n_chunk, (i, j) in enumerate(path):
        t0 = time()
        info = chunk_info[n_chunk]
        rs = info["indices"]["row_start"]
        re = info["indices"]["row_end"]
        cs = info["indices"]["col_start"]
        ce = info["indices"]["col_end"]
        row_size = info["row_size"]
        col_size = info["col_size"]

        logger.info(f"Processing chunk {n_chunk} ({i}, {j}) of {len(path)} total chunks")


        # load A chunk only when row index changed
        if i_prev is None or i != i_prev:
            logger.info(f"Loading A chunk for rows {rs} to {re}")

            # Load A chunk from Dask array
            A_chunk = matrix_da[rs : re + 1, :].astype(dtype_upcast)


        # load B chunk only when col index changed
        if (j_prev is None or j != j_prev) and i != j:
            logger.info(f"Loading B chunk for cols {cs} to {ce}")
            B_chunk = matrix_da[cs : ce + 1, :].astype(dtype_upcast)
        

        # compute block (row_size x col_size)
        if i == j:
             # for diagonal blocks keep only upper-triangular part
            
            logger.info("Calculating block using dask")
            block = da.matmul(A_chunk, A_chunk.T) # type: ignore
            block = da.triu(block)
        else:
            logger.info("Calculating block using dask")
            block = da.matmul(A_chunk, B_chunk.T) # type: ignore

        output[rs : re + 1, cs : ce + 1] = block

        i_prev, j_prev = i, j
        logger.info(
            f"Chunk processed in {time() - t0:.2f} seconds, "
            f"row_size={row_size}, col_size={col_size}"
        )
    client.close()
    cluster.close()
    return output