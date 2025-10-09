import numpy as np
import pytest
from xpcscorr.correlators.dense.reference import correlator, lin_log_bin, lin_bin, bin_ttcf


@pytest.fixture
def create_data():
    
    n_frames=1000
    size_frame=100

    data = np.random.poisson(1000, (n_frames, size_frame, size_frame))

    
    #Some mask
    mask = np.ones((100,100), dtype=np.int8)
    mask[20:80, 20:80] = 1
    
    return data, mask

@pytest.fixture
def calculate_correlator(create_data):

    data, mask = create_data
    g2, g2_err, ttcf = correlator(data, 
                                  mask, 
                                  calculate_g2_err=True, 
                                  calculate_ttcf=True)
    
    return g2, g2_err, ttcf

### Test functions

def test_correlator(calculate_correlator):
    g2, g2_err, ttcf = calculate_correlator
    assert g2 is not None
    assert g2_err is not None
    assert ttcf is not None
    assert g2.shape == (999,)
    assert g2_err.shape == (999,)
    assert ttcf.shape == (1000, 1000)

def test_lin_log_bin():

    x=np.arange(10000)
    N=2
    n_log_bins=100

    bin_edges, bin_indices = lin_log_bin(x, N, n_log_bins)
    assert len(bin_edges) == 10**N+n_log_bins
    assert len(bin_indices) == len(x)
    assert np.max(bin_edges) >= np.max(x)

def test_lin_bin():

    x=np.arange(10000)
    N=100
    bin_edges, bin_indices = lin_bin(x, N)
    assert len(bin_edges) == N
    assert len(bin_indices) == len(x)
    assert np.max(bin_edges) >= np.max(x)

def test_ttcf_bin(create_data,calculate_correlator):
    data , mask = create_data
    _, _,  ttcf = calculate_correlator

    bin_edges_x, _ = lin_log_bin(np.arange(data.shape[0]), 1, 10)
    bin_edges_y, _ = lin_bin(np.arange(data.shape[0]), 100)

    binned_ttcf = bin_ttcf(ttcf, bin_edges_x, bin_edges_y)

    assert binned_ttcf[0].shape == (len(bin_edges_x)-1, len(bin_edges_y)-1)

#TODO: Test the binning of ttcf with age and lag
#def bin_ttcf_age_lag(calculate_correlator):
#    _, _, ttcf = calculate_correlator
#    ttcf_lag_age, lag_bins, age_bins = t1_t2_to_lag_age(ttcf)
    
#    assert ttcf_lag_age.shape == (len(lag_bins)-1, len(age_bins)-1)
    

if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])

   