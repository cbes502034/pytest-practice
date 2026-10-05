"""Unit 5 參考解答"""
import pytest


# 邊界在 4 / 5：4 次是「最後一個不告警」，5 次是「第一個告警」
@pytest.mark.parametrize("count, should_alert", [
    (3, False),
    (4, False),     # 邊界前
    (5, True),      # 邊界
    (6, True),      # 邊界後
    (10, True),
])
def test_failure_threshold(engine, make_event, count, should_alert):
    for t in range(count):
        engine.feed(make_event(ts=t * 5))        # 全部在 60 秒內
    assert (len(engine.alerts) == 1) is should_alert


# 邊界在 300 / 301：規格說「剛好 window 秒仍算在窗內」
@pytest.mark.parametrize("span, should_alert", [
    (240, True),
    (299, True),
    (300, True),    # 剛好在邊界上 → 仍在窗內
    (301, False),   # 超過 1 秒 → 第一筆被擠出窗外，只剩 4 次
    (600, False),
])
def test_time_window_boundary(engine, make_event, span, should_alert):
    for ts in [span * i / 4 for i in range(5)]:
        engine.feed(make_event(ts=ts))
    assert (len(engine.alerts) == 1) is should_alert


@pytest.mark.parametrize("user, severity", [
    ("admin", "high"),
    ("ROOT", "high"),             # 不分大小寫
    ("Administrator", "high"),
    ("alice", "medium"),
    (None, "medium"),             # 沒有帳號資訊
    ("admin_bob", "medium"),      # 陷阱：只是「開頭像」admin，不是特權帳號
], ids=["admin", "uppercase_ROOT", "Administrator", "regular_user", "no_user", "trap_admin_bob"])
def test_severity_by_user(engine, make_event, user, severity):
    for t in range(5):
        engine.feed(make_event(ts=t, user=user))
    assert engine.alerts[0].severity == severity


# 等價類：這三種 action 屬於「不計數」這一類
@pytest.mark.parametrize("action", ["login_success", "conn_blocked", "conn_allowed"])
def test_non_failure_actions_not_counted(engine, make_event, action):
    for t in range(10):
        engine.feed(make_event(ts=t, action=action))
    assert engine.alerts == []
