"""
Unit 2 參考解答

預期結果：3 passed, 1 failed
  - test_action_converted_to_uppercase  → (a) 測試寫錯。規格寫「action 原樣保留，不轉大小寫」→ 修測試
  - test_string_port_converted_to_int  → (b) 產品 bug。規格寫字串 "443" 要轉 int → 保持失敗、寫 bug report
"""
from xvr_lite import parse_event


def test_parse_basic_fields():
    e = parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "login_failed"}')
    assert e["src_ip"] == "45.67.89.10"


# 修正：規格要求 action 原樣保留，所以期望值應該是小寫
def test_action_kept_as_is():
    e = parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "login_failed"}')
    assert e["action"] == "login_failed"


# 不修改 —— 這是產品 bug，讓它保持失敗
def test_string_port_converted_to_int():
    e = parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "conn_blocked", "dst_port": "443"}')
    assert e["dst_port"] == 443


def test_missing_port_is_none():
    e = parse_event('{"ts": 1, "src_ip": "45.67.89.10", "action": "conn_allowed"}')
    assert e["dst_port"] is None


# =====================================================================
# BUG REPORT
#
# 標題：parse_event 收到字串型 dst_port 時未轉為整數
# 嚴重度：中
# 重現步驟：
#   parse_event('{"ts":1,"src_ip":"45.67.89.10","action":"conn_blocked","dst_port":"443"}')
# 預期結果：dst_port == 443（int），依 parse_event 規格
# 實際結果：dst_port == "443"（str）
# 影響範圍：
#   下游若用 dst_port 做比對（例如「連到 22 或 3389 的連線」），
#   "443" == 443 為 False，規則會靜默失效 → 可能造成漏報。
#   只影響會送字串 port 的設備，整數 port 不受影響。
# 重現測試：test_u2_triage.py::test_string_port_converted_to_int
# =====================================================================
