"""Unit 4 參考解答（engine、make_event 在 conftest.py）"""


def test_four_failures_no_alert(engine, make_event):
    for t in (0, 10, 20, 30):
        engine.feed(make_event(ts=t))
    assert engine.alerts == []


def test_five_failures_one_alert(engine, make_event):
    for t in (0, 10, 20, 30, 40):
        engine.feed(make_event(ts=t))

    assert len(engine.alerts) == 1
    alert = engine.alerts[0]
    assert alert.rule == "brute_force"
    assert alert.mitre == "T1110"
    assert alert.count == 5


def test_engine_is_fresh_each_test(engine):
    # 上一個測試產生了 1 則告警；function scope 保證這裡是全新的引擎
    assert engine.alerts == []
    assert engine.events_seen == 0


def test_different_ips_counted_separately(engine, make_event):
    for t in range(3):
        engine.feed(make_event(ts=t, ip="45.67.89.10"))
        engine.feed(make_event(ts=t, ip="91.200.12.34"))
    assert engine.events_seen == 6
    assert engine.alerts == []


def test_success_clears_failures(engine, make_event):
    for t in range(4):
        engine.feed(make_event(ts=t))
    engine.feed(make_event(ts=4, action="login_success"))
    engine.feed(make_event(ts=5))
    assert engine.alerts == []
    # 漏洞：攻擊者如果手上有一組有效帳密，每試 4 次就登入一次，
    #      就能無限試下去而永遠不觸發告警。


def test_no_duplicate_alert_in_cooldown(engine, make_event):
    for t in range(0, 100, 10):      # 10 次
        engine.feed(make_event(ts=t))
    assert len(engine.alerts) == 1
