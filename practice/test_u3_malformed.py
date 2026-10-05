"""
Unit 3 實務練習｜客戶環境的髒資料

【情境】
  XVR 是地端部署產品，裝在客戶機房。客戶的設備五花八門，
  送進來的日誌常常是殘缺的：少欄位、IP 打錯、port 亂填、甚至根本不是 JSON。

  上週有個客戶回報：某台舊設備送了一行亂碼，結果整批日誌都沒進系統。
  團隊決定加強防護，你要寫測試確保：
    1. parse_event 遇到壞資料會丟出「正確的例外」，而且訊息說得出原因
    2. ingest_batch 遇到壞資料會跳過並記錄，不會整批停擺

【你的任務】把下面 7 個測試寫完。全部用 pytest.raises 或檢查 IngestResult。

【跑法】pytest -v test_u3_malformed.py

【驗收】7 passed
"""
import pytest

from xvr_lite import parse_event, ingest_batch, MalformedEvent

GOOD = '{"ts": 1, "src_ip": "45.67.89.10", "action": "login_failed"}'


def test_non_json_raises():
    # TODO：parse_event("這不是json") 要丟 MalformedEvent，訊息含 "JSON"
    assert False, "TODO"


def test_missing_src_ip_raises():
    # TODO：少了 src_ip 欄位 → MalformedEvent，訊息要指出是哪個欄位
    assert False, "TODO"


def test_invalid_ip_raises():
    # TODO：src_ip 是 "999.1.1.1" → MalformedEvent，訊息含 "IP"
    assert False, "TODO"


def test_port_out_of_range_raises():
    # TODO：dst_port 是 70000 → MalformedEvent，訊息含 "port"
    assert False, "TODO"


def test_unknown_action_raises():
    # TODO：action 是 "hack_the_planet" → MalformedEvent
    #       想一想：為什麼不能把未知的 action 默默收下來？
    assert False, "TODO"


def test_batch_skips_bad_lines():
    # TODO：準備一批日誌：3 行好的 + 2 行壞的 + 1 行空白
    #       確認：
    #         - events 有 3 筆
    #         - rejected 是 2（空白行不算）
    #         - reasons 裡有寫出是「第幾行」出錯
    assert False, "TODO"


def test_all_bad_lines_no_exception():
    # TODO：全部都是壞資料時，ingest_batch 不可以丟例外，events 應該是空的
    #       提示：這個測試只要「沒有丟例外而且結果正確」就算通過
    assert False, "TODO"
