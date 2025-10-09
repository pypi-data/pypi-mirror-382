import numpy as np
from xpcscorr.core.utils import (mask_to_3d_bool_stack,
                                rebin2d_bin_edges,
                                rebin2d_bin_indices
                                )


def test_mask_to_3d_bool_stack():
    # 2D binary mask (0/1)
    mask_2d_bin = np.array([[0, 1, 0],
                            [1, 0, 1],
                            [0, 1, 0]])
    out = mask_to_3d_bool_stack(mask_2d_bin)
    assert out.shape == (1, 3, 3)
    assert np.array_equal(out[0], mask_2d_bin.astype(bool))

    # 2D binary mask (all zeros)
    mask_2d_zero = np.zeros((3, 3), dtype=int)
    out = mask_to_3d_bool_stack(mask_2d_zero)
    assert out.shape == (1, 3, 3)
    assert np.all(out == False)

    # 2D boolean mask
    mask_2d_bool = np.array([[True, False, True],
                             [False, True, False],
                             [True, False, True]])
    out = mask_to_3d_bool_stack(mask_2d_bool)
    assert out.shape == (1, 3, 3)
    assert np.array_equal(out[0], mask_2d_bool)

    # 2D integer mask (labels)
    mask_2d_labels = np.array([[0, 2, 1],
                               [1, 2, 0],
                               [2, 1, 0]])
    out = mask_to_3d_bool_stack(mask_2d_labels)
    assert out.shape == (2, 3, 3)  # labels 1 and 2
    assert np.array_equal(out[0], mask_2d_labels == 1)
    assert np.array_equal(out[1], mask_2d_labels == 2)

    # 3D binary mask
    mask_3d_bin = np.zeros((3, 3, 3), dtype=int)
    mask_3d_bin[0, 0, 0] = 1
    mask_3d_bin[1, 1, 1] = 1
    mask_3d_bin[2, 2, 2] = 1
    out = mask_to_3d_bool_stack(mask_3d_bin)
    assert out.shape == (3, 3, 3)
    assert out[0, 0, 0] == True
    assert out[1, 1, 1] == True
    assert out[2, 2, 2] == True
    assert np.sum(out) == 3

    # 3D boolean mask
    mask_3d_bool = np.zeros((3, 3, 3), dtype=bool)
    mask_3d_bool[0, 1, 2] = True
    mask_3d_bool[1, 2, 0] = True
    mask_3d_bool[2, 0, 1] = True
    out = mask_to_3d_bool_stack(mask_3d_bool)
    assert out.shape == (3, 3, 3)
    assert out[0, 1, 2] == True
    assert out[1, 2, 0] == True
    assert out[2, 0, 1] == True
    assert np.sum(out) == 3

    print("All mask_to_3d_bool_stack tests passed.")



def test_xbin_vs_binx():
    '''
    This test two binning approaches, one where input are bin edges and second, where
    input are bin indices.
    '''

    data=np.random.rand(100,100)

    Nx, Ny = data.shape
    binx = np.linspace(0, Nx, 6)
    biny = np.linspace(0, Ny, 6)

    # the -1 is to convert to 0-based indexing
    xbin = np.digitize(np.arange(Nx), binx) - 1  # shape (Nx,) 
    ybin = np.digitize(np.arange(Ny), biny) - 1  # shape (Ny,)

    out_bin_edges = rebin2d_bin_edges(data, binx, biny)
    out_bin_indices = rebin2d_bin_indices(data, xbin, ybin)

    # there are n edges but n-1 bins
    nx = len(binx) - 1
    ny = len(biny) - 1
    out_bin_indices = out_bin_indices[:nx, :ny]

    assert np.allclose(out_bin_edges, out_bin_indices, atol=1e-12), "rebin2d with bin edges and bin indices results differ!"
    
