"""
Unit 1 實務練習｜新日誌來源上線前的驗證

【情境】
  客戶的 SOC 要接上一台新的防火牆，它會吐出 JSON 格式的登入與連線日誌。
  開發同事已經寫好 parse_event()，在接進正式環境之前，主管請你先寫測試，
  確認「正常的日誌」都能被正確解析成標準格式。

  規格請看 xvr_lite.py 的 parse_event docstring。

【你的任務】把下面 5 個測試寫完。

【跑法】
  cd practice
  pytest -v test_u1_parse.py

【驗收】5 passed
"""
from xvr_lite import parse_event

# 這行是防火牆實際送來的一筆日誌，可以直接拿來用
SAMPLE = '{"ts": 1700000000, "src_ip": "45.67.89.10", "action": "login_failed", "user": "admin", "dst_port": 22}'

def test_basic_fields_parsed():
    # TODO：解析 SAMPLE，確認 src_ip、action、user 三個欄位跟原始日誌一致
    event = parse_event(SAMPLE)
    assert event['src_ip'] == "45.67.89.10"
    assert event['action'] == "login_failed"
    assert event['user'] == "admin"

def test_ts_converted_to_float():
    # TODO：原始的 ts 是整數 1700000000，解析後應該是 float
    #       提示：isinstance(x, float)
    event = parse_event(SAMPLE)
    assert isinstance(event['ts'], float)
    assert event['ts'] == 1700000000.0


def test_missing_user_is_none():
    # TODO：自己寫一行沒有 user 的日誌，確認解析後 user 是 None
    line = '{"ts": 1700000000, "src_ip": "45.67.89.10", "action": "login_failed", "dst_port": 22}'
    event = parse_event(line)
    assert event['user'] is None


def test_int_port_stays_int():
    # TODO：SAMPLE 的 dst_port 是 22，解析後應該還是整數 22
    event = parse_event(SAMPLE)
    assert event['dst_port'] == 22


def test_ipv6_source_supported():
    # TODO：src_ip 換成 IPv6，例如 "2001:db8::1"，應該能正常解析，不丟例外
    line = '{"ts":"1700000000", "src_ip":"2001:db8::1", "action":"login_failed"}'
    event = parse_event(line)
    assert event['src_ip'] == "2001:db8::1"
