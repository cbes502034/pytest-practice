"""Unit 1 參考解答"""
from xvr_lite import parse_event

SAMPLE = '{"ts": 1700000000, "src_ip": "45.67.89.10", "action": "login_failed", "user": "admin", "dst_port": 22}'


def test_basic_fields_parsed():
    e = parse_event(SAMPLE)
    assert e["src_ip"] == "45.67.89.10"
    assert e["action"] == "login_failed"
    assert e["user"] == "admin"


def test_ts_converted_to_float():
    e = parse_event(SAMPLE)
    assert isinstance(e["ts"], float)
    assert e["ts"] == 1700000000.0


def test_missing_user_is_none():
    e = parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "conn_blocked"}')
    assert e["user"] is None          # 用 is None，不要用 == None


def test_int_port_stays_int():
    e = parse_event(SAMPLE)
    assert e["dst_port"] == 22
    assert isinstance(e["dst_port"], int)


def test_ipv6_source_supported():
    e = parse_event('{"ts": 1, "src_ip": "2001:db8::1", "action": "login_failed"}')
    assert e["src_ip"] == "2001:db8::1"
