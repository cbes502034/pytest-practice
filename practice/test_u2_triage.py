"""
Unit 2 實務練習｜CI 亮紅燈，你負責分診

【情境】
  早上 9 點，CI 通知 parse_event 的測試失敗了。這四個測試是前一位同事寫的。
  測試失敗只有兩種可能：
     (a) 測試寫錯了 —— 期望值跟規格不符
     (b) 產品有 bug —— 程式行為跟規格不符
  判斷依據只有一個：xvr_lite.py 裡 parse_event 的 docstring（規格）。

【你的任務】
  1. 先跑：pytest -v test_u2_triage.py，讀懂每一個失敗訊息
  2. 對每個失敗，判斷是 (a) 還是 (b)
  3. 屬於 (a) 的：修改「測試」讓它符合規格
  4. 屬於 (b) 的：⚠️ 不要改 xvr_lite.py，也不要改測試去配合錯誤行為。
     讓它保持失敗，在檔案最下方的 BUG REPORT 區塊寫一份簡短的 bug 回報

【驗收】3 passed, 1 failed，而且 bug 回報寫得出「重現步驟、預期、實際」
"""
from xvr_lite import parse_event


def test_parse_basic_fields():
    e = parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "login_failed"}')
    assert e["src_ip"] == "45.67.89.10"


def test_action_converted_to_uppercase():
    e = parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "login_failed"}')
    assert e["action"] == "LOGIN_FAILED"


def test_string_port_converted_to_int():
    e = parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "conn_blocked", "dst_port": "443"}')
    assert e["dst_port"] == 443


def test_missing_port_is_none():
    e = parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "conn_allowed"}')
    assert e["dst_port"] is None


# =====================================================================
# BUG REPORT（請填寫）
#
# 標題：
# 嚴重度：
# 重現步驟：
# 預期結果：
# 實際結果：
# 影響範圍：（這個 bug 會讓下游哪些東西出問題？）
# =====================================================================
