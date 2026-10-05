"""
Unit 4 實務練習｜測試一條有「記憶」的偵測規則

【情境】
  Detection Engineering 團隊剛寫好一條「暴力破解偵測」規則（對應 MITRE ATT&CK T1110）：
      同一個來源 IP，5 分鐘內登入失敗 5 次 → 告警

  這條規則跟 Unit 1-3 不一樣：它有「狀態」。它會記住每個 IP 失敗過幾次。
  所以每個測試開始時，偵測引擎一定要是乾淨的 —— 否則上一個測試留下的紀錄，
  會讓下一個測試莫名其妙地觸發告警。

  規格請看 xvr_lite.py 的 BruteForceRule docstring。

【你的任務】
  1. 先到 conftest.py 完成 TODO 4-1（engine）和 4-2（make_event）
  2. 回來把下面 6 個測試寫完

【跑法】pytest -v -s test_u4_fixture.py

【驗收】6 passed
"""


def test_four_failures_no_alert(engine, make_event):
    # TODO：同一個 IP 在 60 秒內失敗 4 次（ts = 0, 10, 20, 30）
    #       engine.alerts 應該是空的
    assert False, "TODO"


def test_five_failures_one_alert(engine, make_event):
    # TODO：失敗 5 次，engine.alerts 應該剛好 1 則
    #       並檢查這則告警的 rule == "brute_force"、mitre == "T1110"、count == 5
    assert False, "TODO"


def test_engine_is_fresh_each_test(engine):
    # TODO：上一個測試產生了告警。如果 fixture 寫對了，這裡的 engine 應該是全新的
    #       檢查 engine.alerts 是空的、engine.events_seen 是 0
    assert False, "TODO"


def test_different_ips_counted_separately(engine, make_event):
    # TODO：IP A 失敗 3 次、IP B 失敗 3 次（合計 6 次，但各自都沒到 5）
    #       不應該產生告警
    assert False, "TODO"


def test_success_clears_failures(engine, make_event):
    # TODO：失敗 4 次 → 成功 1 次 → 再失敗 1 次
    #       不應該告警（成功之後重新計算）
    #       想一想：這條規則對真實攻擊有什麼漏洞？
    assert False, "TODO"


def test_no_duplicate_alert_in_cooldown(engine, make_event):
    # TODO：同一個 IP 在 100 秒內連續失敗 10 次
    #       應該只產生 1 則告警，而不是 6 則
    assert False, "TODO"
