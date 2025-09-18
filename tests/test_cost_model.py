from funding import model


def test_compute_edge_bps():
    edge = model.compute_edge_bps(funding_bps=12.5, fee_bps=7.0, slippage_bps=2.0)
    assert edge == 3.5


def test_expected_pnl_usdt():
    pnl = model.expected_pnl_usdt(notional=2000, edge_bps=5)
    assert round(pnl, 4) == 1.0


def test_should_open_position():
    assert model.should_open_position(edge_bps=0.6, threshold_bps=0.5) is True
    assert model.should_open_position(edge_bps=0.4, threshold_bps=0.5) is False
