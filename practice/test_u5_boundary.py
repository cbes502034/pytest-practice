"""
Unit 5 實務練習｜誤報與漏報的分界線

【情境】
  公司的研發計畫目標之一是「降低誤報率」。
  客戶抱怨：「每天都收到一堆暴力破解告警，點進去看都只是員工忘記密碼。」
  另一位客戶則說：「我們被打了，你們的系統卻沒叫。」

  兩個抱怨都指向同一件事：偵測規則的「門檻」和「時間窗」。
  門檻太低 → 誤報（False Positive）；太高 → 漏報（False Negative）。
  任何一點點邊界寫錯，都會直接反映在客戶的告警量上。

  主管要你用 parametrize 把這條規則的所有邊界一次釘死。
  未來有人調整門檻，這組測試會立刻告訴他影響了什麼。

【你的任務】把下面 4 個測試改寫成 parametrize 版本。

【跑法】pytest -v test_u5_boundary.py

【驗收】19 個測試通過（4 個函式，parametrize 展開後 5 + 5 + 6 + 3 = 19）
"""
import pytest


def test_failure_threshold(engine, make_event):
    # TODO：parametrize「失敗次數」與「是否告警」
    #       至少測：3, 4, 5, 6, 10 次（都在 60 秒內發生）
    #       哪幾個是邊界？
    assert False, "TODO"


def test_time_window_boundary(engine, make_event):
    # TODO：同一個 IP 失敗 5 次，平均分散在 span 秒內
    #       （第一次在 0 秒，最後一次在 span 秒）
    #       parametrize span：240, 299, 300, 301, 600
    #       哪些會告警？規格說「剛好 window 秒仍算在窗內」
    #
    #       提示：時間點可以用 [span * i / 4 for i in range(5)]
    assert False, "TODO"


def test_severity_by_user(engine, make_event):
    # TODO：parametrize「觸發告警的帳號」與「期望嚴重度」，並用 ids 命名
    #       至少測：admin, ROOT, Administrator, alice, None, admin_bob
    #       最後一個是陷阱 —— 想清楚它應該是什麼
    assert False, "TODO"


def test_non_failure_actions_not_counted(engine, make_event):
    # TODO：parametrize action：login_success, conn_blocked, conn_allowed
    #       同一個 IP 送 10 筆該 action 的事件，都不應該告警
    #       這是「等價類劃分」：這三種 action 屬於同一類（不計數）
    assert False, "TODO"
