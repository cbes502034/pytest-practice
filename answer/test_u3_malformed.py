"""Unit 3 參考解答"""
import json

import pytest

from xvr_lite import parse_event, ingest_batch, MalformedEvent

GOOD = '{"ts": 1, "src_ip": "45.67.89.10", "action": "login_failed"}'


def test_non_json_raises():
    with pytest.raises(MalformedEvent, match="JSON"):
        parse_event("這不是json")


def test_missing_src_ip_raises():
    with pytest.raises(MalformedEvent, match="src_ip"):
        parse_event('{"ts": 1, "action": "login_failed"}')


def test_invalid_ip_raises():
    with pytest.raises(MalformedEvent, match="IP"):
        parse_event('{"ts": 1, "src_ip": "999.1.1.1", "action": "login_failed"}')


def test_port_out_of_range_raises():
    with pytest.raises(MalformedEvent, match="port"):
        parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "conn_blocked", "dst_port": 70000}')


def test_unknown_action_raises():
    # 未知 action 不能默默收下：偵測規則只認得清單內的 action，
    # 收下一個沒人認得的事件，等於讓它從所有規則旁邊溜過去。
    with pytest.raises(MalformedEvent, match="action"):
        parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "hack_the_planet"}')


def test_batch_skips_bad_lines():
    lines = [
        GOOD,                                   # 第 1 行
        "亂碼@@@",                              # 第 2 行 ✗
        GOOD,                                   # 第 3 行
        "",                                     # 第 4 行 空白，不算
        json.dumps({"ts": 1, "action": "x"}),   # 第 5 行 ✗ 缺 src_ip
        GOOD,                                   # 第 6 行
    ]
    result = ingest_batch(lines)

    assert len(result.events) == 3
    assert result.rejected == 2
    assert "第 2 行" in result.reasons[0]
    assert "第 5 行" in result.reasons[1]


def test_all_bad_lines_no_exception():
    result = ingest_batch(["???", "{", "not json at all"])
    assert result.events == []
    assert result.rejected == 3
