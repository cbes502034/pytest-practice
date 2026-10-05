"""Unit 7 參考解答"""
import json

import pytest

from xvr_lite import Alert, Responder, FirewallError, ingest_batch, DetectionEngine

PUBLIC_IP = "91.200.12.34"


def make_alert(ip=PUBLIC_IP, severity="high"):
    return Alert(rule="brute_force", src_ip=ip, severity=severity,
                 mitre="T1110", ts=0.0, count=5, user="admin")


class FakeFirewall:
    """假防火牆：記錄每次呼叫，並可模擬三種結果。"""

    def __init__(self, mode="ok"):
        self.mode = mode          # "ok" / "reject" / "error"
        self.calls = []

    def block(self, ip, reason):
        self.calls.append((ip, reason))
        if self.mode == "error":
            raise FirewallError("連線逾時")
        if self.mode == "reject":
            return {"ok": False}
        return {"ok": True}


def test_high_severity_blocks():
    fw = FakeFirewall()
    result = Responder(fw).handle(make_alert())

    assert result == "blocked"
    assert len(fw.calls) == 1
    ip, reason = fw.calls[0]
    assert ip == PUBLIC_IP
    assert "T1110" in reason


def test_medium_severity_only_notifies():
    fw = FakeFirewall()
    result = Responder(fw).handle(make_alert(severity="medium"))

    assert result == "notified"
    assert fw.calls == []        # ⭐ 檢查「沒有發生的事」


def test_allowlisted_ip_never_blocked():
    fw = FakeFirewall()
    result = Responder(fw, allowlist={"8.8.8.8"}).handle(make_alert(ip="8.8.8.8"))

    assert result == "skipped"
    assert fw.calls == []


# 內網 IP 通常是客戶自己的機器（被入侵的主機、甚至是 AD 伺服器）。
# 自動封鎖可能讓整個內網服務中斷，必須交給人判斷。
@pytest.mark.parametrize("ip", ["10.0.0.5", "172.16.0.9", "192.168.1.20"])
def test_private_ip_never_blocked(ip):
    fw = FakeFirewall()
    result = Responder(fw).handle(make_alert(ip=ip))

    assert result == "skipped"
    assert fw.calls == []


def test_firewall_error_does_not_crash():
    fw = FakeFirewall(mode="error")
    responder = Responder(fw)
    alert = make_alert()

    result = responder.handle(alert)        # 沒有 pytest.raises —— 不該丟例外

    assert result == "block_failed"
    assert alert in responder.pending_review


def test_firewall_rejects():
    fw = FakeFirewall(mode="reject")
    responder = Responder(fw)
    alert = make_alert()

    assert responder.handle(alert) == "block_failed"
    assert alert in responder.pending_review


def test_end_to_end_pipeline():
    lines = [
        json.dumps({"ts": t, "src_ip": PUBLIC_IP, "action": "login_failed", "user": "admin"})
        for t in range(6)
    ]
    lines.insert(3, "%%%亂碼%%%")

    batch = ingest_batch(lines)
    engine = DetectionEngine()
    alerts = engine.feed_many(batch.events)
    fw = FakeFirewall()
    responder = Responder(fw)
    results = [responder.handle(a) for a in alerts]

    assert batch.rejected == 1
    assert len(alerts) == 1
    assert results == ["blocked"]
    assert fw.calls[0][0] == PUBLIC_IP
