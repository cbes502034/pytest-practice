"""
Unit 6 實務練習｜告警品質回歸套件

【情境】
  資安分析師在處理客戶告警時，回報了兩個問題：

  ① 誤報（False Positive）
     客戶的備份服務帳號 svc_backup 每天凌晨會因為密碼輪替失敗重試很多次，
     每晚都觸發「暴力破解」告警。正確行為應該是：svc_ 開頭的服務帳號不告警。
     規則還沒改，排在下個版本。

  ② 漏報（False Negative）
     攻擊者用 5 個不同 IP，各試一次 admin 的密碼（分散式暴力破解）。
     目前規則只看「同一個 IP」，所以完全沒偵測到。也還沒修。

  主管要求：這兩個已知問題要「留在測試套件裡」持續追蹤，但不能讓 CI 一直紅。
  另外，套件裡有一個很慢的效能測試，開發時希望能跳過。

【你的任務】
  1. 先到 conftest.py 完成 TODO 6-1（註冊 detection 和 slow 兩個 marker）
  2. 下面每個測試已經寫好了，你要做的是「加上正確的 marker」

【跑法】
  pytest -v test_u6_markers.py
  pytest -v -m "not slow" test_u6_markers.py
  pytest -v -m "detection" test_u6_markers.py

【驗收】
  pytest -v test_u6_markers.py   → 3 passed, 1 skipped, 2 xfailed（Windows 上）
  -m "not slow"                  → 多一個 deselected
"""
import sys
import time

import pytest

from xvr_lite import DetectionEngine


# TODO 6-2：這是效能測試，很慢。加上 slow marker
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


# TODO 6-3：這是已知誤報，還沒修。用 xfail 標記，reason 要寫清楚
#           並加上 detection marker
def test_service_account_no_alert(engine, make_event):
    for t in range(0, 50, 10):
        engine.feed(make_event(ts=t, user="svc_backup"))
    assert engine.alerts == []


# TODO 6-4：這是已知漏報，還沒修。用 xfail 標記，並加上 detection marker
def test_distributed_brute_force_detected(engine, make_event):
    ips = ["45.67.89.1", "45.67.89.2", "45.67.89.3", "45.67.89.4", "45.67.89.5"]
    for t, ip in enumerate(ips):
        engine.feed(make_event(ts=t, ip=ip, user="admin"))
    assert len(engine.alerts) == 1


# TODO 6-5：這個測試讀的是 Linux 的系統日誌路徑，在 Windows 上沒意義
#           用 skipif 讓它在 Windows 上自動跳過
def test_linux_log_dir_exists():
    import os
    assert os.path.exists("/var/log")


# TODO 6-6：加上 detection marker（這兩個是正常的偵測測試）
def test_basic_brute_force_detection(engine, make_event):
    for t in range(5):
        engine.feed(make_event(ts=t))
    assert len(engine.alerts) == 1


def test_successful_login_no_alert(engine, make_event):
    engine.feed(make_event(ts=0, action="login_success"))
    assert engine.alerts == []


# =====================================================================
# 💡 做完想一想
#   1. 為什麼 ① ② 用 xfail 而不是 skip？
#   2. 哪天有人把 svc_ 帳號的例外處理做好了，test_service_account_no_alert 會變成什麼狀態？
#   3. 誤報和漏報，哪一個對客戶傷害比較大？（沒有標準答案，但面試很可能問）
# =====================================================================
