"""
Unit 7 實務練習｜自動封鎖，但絕對不能封錯

【情境】
  XVR 的賣點之一是「主動防禦」：偵測到高風險攻擊時，自動通知防火牆封鎖來源 IP。
  這個功能很強，但也很危險 —— 封錯一個 IP，客戶的服務可能就斷了。

  所以 Responder 的設計刻意把「判斷」和「執行」分開：
    Responder 負責決定「要不要封」，FirewallClient 負責「真的去封」。

  你的任務是驗證 Responder 的判斷邏輯完全正確。
  ⚠️ 測試中絕對不能呼叫真實的 FirewallClient（呼叫了會直接丟 RuntimeError）。
     你要自己做一個假的防火牆，注入進去。

  規格請看 xvr_lite.py 的 Responder docstring。

【你的任務】
  1. 寫一個假防火牆類別，要能記錄「被呼叫了幾次、參數是什麼」
     而且要能模擬三種狀況：成功、回傳失敗、丟出 FirewallError
  2. 把下面 7 個測試寫完

【跑法】pytest -v test_u7_responder.py

【驗收】全部通過（含 parametrize 展開）
"""
import pytest

from xvr_lite import Alert, Responder, FirewallError

PUBLIC_IP = "91.200.12.34"


def make_alert(ip=PUBLIC_IP, severity="high"):
    """快速做出一則告警。"""
    return Alert(rule="brute_force", src_ip=ip, severity=severity,
                 mitre="T1110", ts=0.0, count=5, user="admin")


# ---------------------------------------------------------------------
# TODO 7-1：假防火牆
#   需求：
#     - 有 block(self, ip, reason) 方法
#     - 把每次呼叫記錄下來（例如 self.calls = [(ip, reason), ...]）
#     - 建構時可以指定模式：成功 / 回傳 {"ok": False} / 丟 FirewallError
# ---------------------------------------------------------------------
class FakeFirewall:
    pass


def test_high_severity_blocks():
    # TODO：handle() 回傳 "blocked"，firewall 被呼叫 1 次，ip 正確，
    #       reason 裡要有 MITRE 編號 "T1110"
    assert False, "TODO"


def test_medium_severity_only_notifies():
    # TODO：severity="medium" → 回傳 "notified"，而且 firewall「一次都沒被呼叫」
    #       ⭐ 這題的重點在後半句
    assert False, "TODO"


def test_allowlisted_ip_never_blocked():
    # TODO：8.8.8.8 在 allowlist，就算是 high 也回傳 "skipped"，firewall 沒被呼叫
    assert False, "TODO"


def test_private_ip_never_blocked():
    # TODO：用 parametrize 測 10.0.0.5、172.16.0.9、192.168.1.20
    #       全部回傳 "skipped"，firewall 沒被呼叫
    #       想一想：為什麼內網 IP 不能自動封鎖？
    assert False, "TODO"


def test_firewall_error_does_not_crash():
    # TODO：假防火牆丟 FirewallError
    #       handle() 不可以把例外往外丟，要回傳 "block_failed"
    #       而且這則告警要出現在 responder.pending_review
    assert False, "TODO"


def test_firewall_rejects():
    # TODO：假防火牆回傳 {"ok": False}
    #       → "block_failed"，告警進 pending_review
    assert False, "TODO"


def test_end_to_end_pipeline():
    # TODO：⭐ 綜合題，把整條管線串起來
    #   1. 準備原始日誌：同一個公網 IP 用 admin 帳號失敗 6 次 + 1 行亂碼
    #   2. ingest_batch → DetectionEngine.feed_many → 每則告警交給 Responder
    #   3. 驗證：rejected 是 1、告警 1 則、防火牆被呼叫 1 次、結果是 "blocked"
    #
    #   提示：from xvr_lite import ingest_batch, DetectionEngine
    #         日誌可以用 json.dumps({...}) 產生
    assert False, "TODO"
