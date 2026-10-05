"""Unit 6 參考解答（marker 註冊在 conftest.py）"""
import os
import sys
import time

import pytest

from xvr_lite import DetectionEngine


@pytest.mark.slow
def test_50k_events_within_3_seconds():
    engine = DetectionEngine()
    events = [
        {"ts": float(i), "src_ip": f"45.67.{i % 200}.{i % 250}", "action": "login_failed",
         "user": "alice", "dst_port": 22}
        for i in range(50_000)
    ]
    start = time.perf_counter()
    engine.feed_many(events)
    assert time.perf_counter() - start < 3.0


@pytest.mark.detection
@pytest.mark.xfail(reason="已知誤報：svc_ 服務帳號的重試會觸發暴力破解告警，預計下版加入例外")
def test_service_account_no_alert(engine, make_event):
    for t in range(0, 50, 10):
        engine.feed(make_event(ts=t, user="svc_backup"))
    assert engine.alerts == []


@pytest.mark.detection
@pytest.mark.xfail(reason="已知漏報：規則只以單一來源 IP 計數，偵測不到分散式暴力破解")
def test_distributed_brute_force_detected(engine, make_event):
    ips = ["45.67.89.1", "45.67.89.2", "45.67.89.3", "45.67.89.4", "45.67.89.5"]
    for t, ip in enumerate(ips):
        engine.feed(make_event(ts=t, ip=ip, user="admin"))
    assert len(engine.alerts) == 1


@pytest.mark.skipif(sys.platform == "win32", reason="Linux 系統日誌路徑，Windows 上無意義")
def test_linux_log_dir_exists():
    assert os.path.exists("/var/log")


@pytest.mark.detection
def test_basic_brute_force_detection(engine, make_event):
    for t in range(5):
        engine.feed(make_event(ts=t))
    assert len(engine.alerts) == 1


@pytest.mark.detection
def test_successful_login_no_alert(engine, make_event):
    engine.feed(make_event(ts=0, action="login_success"))
    assert engine.alerts == []
