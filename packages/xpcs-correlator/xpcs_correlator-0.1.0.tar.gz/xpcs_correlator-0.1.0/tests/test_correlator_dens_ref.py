import pytest
import numpy as np

from xpcscorr import correlator_dense_reference
                                                  

@pytest.fixture
def create_data():
    
    n_frames=1000
    size_frame=100

    data = np.random.poisson(1000, (n_frames, size_frame, size_frame))

    
    #Some mask
    mask = np.ones((100,100), dtype=np.int8)
    mask[20:80, 20:80] = 1
    mask[0:10, 90:100] = 2
    
    return data, mask

def test_correlator_dense_reference(create_data):
    data, mask = create_data
    result = correlator_dense_reference(data, mask, ttcf_format='t1,t2')
    
    assert len(result.g2) == 2
    assert result.g2[1].shape[0] == data.shape[0]-1
    assert len(result.g2_err) == 2
    assert result.g2_err[1].shape[0] == data.shape[0]-1
    assert len(result.ttcf) == 2
    assert result.ttcf[1].shape == (1000, 1000)


def test_correlator_dense_reference_lin_binning(create_data):
    data, mask = create_data
    
    result = correlator_dense_reference(data, mask, ttcf_format='t1,t2', t1_t2_binning=100)
    assert result.ttcf[0].shape == (100, 100)


def test_correlator_dense_reference_log_binning(create_data):
    data, mask = create_data

    lag_binning = (2, 5)  # linear to 10, then 5 bins 
    age_binning = 50      # 50 linear bins

    result= correlator_dense_reference(data, mask, 
                                       ttcf_format='age,lag', 
                                       age_binning=age_binning, 
                                       lag_binning=lag_binning)
    assert result.ttcf[0].shape == (50, 99+5)
    assert result.age.shape[0] == 50
    assert result.lag.shape[0] == 99+5
    
    
