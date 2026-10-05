"""
conftest.py —— pytest 自動載入，不需要 import。

這個檔案你會回來改兩次：
  Unit 4：加入 fixture
  Unit 6：註冊自訂 marker
"""
import pytest

from xvr_lite import DetectionEngine, BruteForceRule


# ---------------------------------------------------------------------
# TODO (Unit 4-1)：fixture `engine`
#   - 建立 DetectionEngine([BruteForceRule(threshold=5, window=300)])
#   - 用 yield 交給測試
#   - 測試結束後呼叫 .reset()
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# TODO (Unit 4-2)：fixture `make_event`（工廠型 fixture）
#   回傳「一個函式」，讓測試可以快速做出事件，例如：
#       make_event(ts=0)                          -> 預設 IP、login_failed、user="alice"
#       make_event(ts=10, user="admin")
#       make_event(ts=20, ip="91.200.12.34", action="login_success")
#   回傳的 dict 要長得跟 parse_event 的輸出一樣：
#       {"ts": float, "src_ip": str, "action": str, "user": ..., "dst_port": 22}
#   預設 IP 請用 "45.67.89.10"
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# TODO (Unit 6-1)：註冊自訂 marker `detection` 和 `slow`
#
# def pytest_configure(config):
#     config.addinivalue_line("markers", "...")
# ---------------------------------------------------------------------
