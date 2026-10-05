"""參考解答的 conftest（Unit 4 的 fixture、Unit 6 的 marker 都在這裡）"""
import sys
from pathlib import Path

import pytest

# 讓 answer/ 底下的測試 import 得到 practice/xvr_lite.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "practice"))

from xvr_lite import DetectionEngine, BruteForceRule  # noqa: E402


# ---- Unit 6-1：註冊自訂 marker ---------------------------------------
def pytest_configure(config):
    config.addinivalue_line("markers", "detection: 偵測規則相關的測試")
    config.addinivalue_line("markers", "slow: 跑比較久的測試，開發時可跳過")


# ---- Unit 4-1：每個測試一個乾淨的偵測引擎 ----------------------------
@pytest.fixture
def engine():
    eng = DetectionEngine([BruteForceRule(threshold=5, window=300)])
    yield eng
    eng.reset()


# ---- Unit 4-2：工廠型 fixture —— 回傳「做事件的函式」 -----------------
@pytest.fixture
def make_event():
    def _make(ts, ip="45.67.89.10", action="login_failed", user="alice"):
        return {"ts": float(ts), "src_ip": ip, "action": action,
                "user": user, "dst_port": 22}
    return _make
