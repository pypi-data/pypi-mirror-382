import numpy as np

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
        num_chunks (int): Number of chunks per row dimension - frames.
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


class MatrixChunking:
    def __init__(self, data, 
                 num_chunks, 
                 matrix_dtype=np.int8,
                 chunk_dtype=np.float32,
                 output_dtype=np.float32):

        if isinstance(data, np.ndarray):
            self.data_shape = data.shape
            self.matrix_dtype = data.dtype

        elif isinstance(data, tuple):
            self.data_shape = data
            self.matrix_dtype = matrix_dtype

        else:
            raise ValueError("data must be a numpy array or a tuple representing the shape")

        self.chunk_dtype = chunk_dtype
        self.output_dtype = output_dtype
        self.num_chunks = num_chunks

        self.path = list(upper_triangle_snake(num_chunks))
        self.chunks_to_process = {}
        
        self._calculate_parameters()
        

    def info_chunk(self):
        print("MatrixChunking Info:")
        for chunk_num, info in self.chunks_info.items():
            print(f"  Chunk {chunk_num}:")
            for key, value in info.items():
                print(f"    {key}: {value}")
    
    def info_summary(self):
        total_chunks = len(self.chunks_info)
        total_elements = sum(info["total_elements"] for info in self.chunks_info.values())
        print(f"MatrixChunking Summary:")
        print(f"  Total Chunks: {total_chunks}")
        print(f"  Total Elements: {total_elements}")

    def info_chunk_size(self):

        for i in range(len(self.chunks_info)):
            n_chunk = i
            chunk_size = self._chunk_size(n_chunk)
            if chunk_size is not None:
                print(f"  Chunk {n_chunk} Size: {chunk_size:.6f} GB")

    def info_data_to_process(self):
        for chunk_num, info in self.chunks_to_process.items():
            print(f"  Process chunk {chunk_num}:")
            for key, value in info.items():
                if key in ("data_size_i", "data_size_j"):
                    gb_value = value / (1024 ** 3)
                    print(f"    {key}: {gb_value:.3f} GB (dtype: {np.dtype(self.chunk_dtype).name})")
                elif key == "output_size":
                    gb_value = value / (1024 ** 3)
                    print(f"    {key}: {gb_value:.3f} GB (dtype: {np.dtype(self.output_dtype).name})")
                else:
                    print(f"    {key}: {value}")

    def info_input_matrix(self):
        print("Input Matrix Info:")
        print(f"  Shape: {self.data_shape}")
        print(f"  Size: {self._input_matrix_size() / (1024 ** 3):.3f} GB (dtype: {np.dtype(self.matrix_dtype).name})")

    def info_output_matrix(self):
        print("Output Matrix Info:")
        print(f"  Shape: {self.data_shape[0]} x {self.data_shape[0]}")
        print(f"  Size: {self._output_matrix_size() / (1024 ** 3):.3f} GB (dtype: {np.dtype(self.output_dtype).name})")


    def _input_matrix_size(self):
        return self.data_shape[0] * self.data_shape[1] * np.dtype(self.matrix_dtype).itemsize

    def _output_matrix_size(self):
        return self.data_shape[0] ** 2 * np.dtype(self.output_dtype).itemsize

    def _chunk_size(self,n_chunk):
        """
        Get the size of a specific chunk in GB.

        Args:
            n_chunk (int): The chunk number.

        Returns:
            float: Size of the chunk in GB.
        """
        chunk_info = get_chunks_info(self.data_shape[0], self.num_chunks).get(n_chunk)

        if chunk_info:
            row_size = chunk_info["row_size"]
            col_size = chunk_info["col_size"]
            # Assuming the data type is float32 (4 bytes)
            chunk_size = row_size * col_size * 4 / (1024 ** 3)  # Convert to GB
            return chunk_size

    #self.chunks_info = get_chunks_info(self.data_shape[0], num_chunks)
    

    

    def _calculate_parameters(self):
        self._get_chunks_info()
        self._chunks_to_process()
        self._data_to_process()


    def _get_chunks_info(self):
        chunks = get_chunks_info(self.data_shape[0], self.num_chunks)
        self.chunks_info = chunks  # <-- Add this line
        for key, values in chunks.items():
            self.chunks_to_process[key] = {}
            self.chunks_to_process[key]['row_size'] = values['row_size']
            self.chunks_to_process[key]['col_size'] = values['col_size']
            self.chunks_to_process[key]['total_elements'] = values['total_elements']

    def _chunks_to_process(self):
        for chunk_number, (i, j) in enumerate(self.path):
            if chunk_number not in self.chunks_to_process:
                self.chunks_to_process[chunk_number] = {}
            self.chunks_to_process[chunk_number]['chunks'] = (i, j)

    def _data_to_process(self):

        for chunk_number, (i, j) in enumerate(self.path):
            bytes_per_element = np.dtype(self.chunk_dtype).itemsize # type: ignore
            data_size_i = self.chunks_to_process[chunk_number]["row_size"] * self.data_shape[1] * bytes_per_element
            data_size_j = self.chunks_to_process[chunk_number]["col_size"] * self.data_shape[1] * bytes_per_element
            self.chunks_to_process[chunk_number]['data_size_i'] = data_size_i
            self.chunks_to_process[chunk_number]['data_size_j'] = data_size_j
            self.chunks_to_process[chunk_number]['output_size'] = self.chunks_to_process[chunk_number]['row_size'] \
                                                                    * self.chunks_to_process[chunk_number]['col_size'] \
                                                                        * np.dtype(self.output_dtype).itemsize

