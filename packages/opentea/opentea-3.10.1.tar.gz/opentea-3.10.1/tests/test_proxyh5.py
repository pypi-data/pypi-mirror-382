import pytest

from opentea.tools.proxy_h5 import ProxyH5


def test_proxyh5(datadir):

    msh_file = datadir.join("trappedvtx_reloaded.mesh.h5")
    msh_ = ProxyH5(msh_file)
    vol_dom = msh_.get_field("vol_domain")
    print(vol_dom)
    assert vol_dom[0] == 0.0004794414857740585
