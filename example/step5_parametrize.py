"""
=====================================================================
 第 5 步：parametrize —— 同一個測試，很多組資料
=====================================================================

跑法：
    pytest -v step5_parametrize.py

⭐ 這一步最重要。面試問「你怎麼設計測試案例」的時候，答案就在這裡。
"""

import pytest

from cart import ShoppingCart


# =====================================================================
# 【問題】三個折扣碼，寫了三個幾乎一模一樣的測試
# =====================================================================
def test_old_save10():
    cart = ShoppingCart()
    cart.add("蘋果", price=100)
    assert cart.total("SAVE10") == 90


def test_old_save20():
    cart = ShoppingCart()
    cart.add("蘋果", price=100)
    assert cart.total("SAVE20") == 80


def test_old_half():
    cart = ShoppingCart()
    cart.add("蘋果", price=100)
    assert cart.total("HALF") == 50


# 差別只有兩個字串和兩個數字，其他完全一樣。


# =====================================================================
# 【解法】parametrize
#
# 把「會變的東西」拉出來變成參數，列成一張表。
# =====================================================================
@pytest.mark.parametrize("code, expected_price", [
    ("SAVE10", 90),
    ("SAVE20", 80),
    ("HALF", 50),
])
def test_new_discount_codes(code, expected_price):
    cart = ShoppingCart()
    cart.add("蘋果", price=100)
    assert cart.total(code) == expected_price


# =====================================================================
# 【重點】每一組參數是「獨立的一個測試」
#
# 跑 pytest -v 會看到：
#     test_new_discount_codes[SAVE10-90] PASSED
#     test_new_discount_codes[SAVE20-80] PASSED
#     test_new_discount_codes[HALF-50]   PASSED
#
# 三行，不是一行。所以哪一組掛掉你立刻知道。
# 這跟「在測試裡寫一個 for 迴圈」完全不同 ——
# 用 for 的話第一組失敗就停了，後面根本不會跑。
# =====================================================================


# =====================================================================
# 【實戰】用 parametrize 做「邊界值分析」
#
# 這是測試設計的基本功。先解釋兩個名詞：
#
#   等價類劃分：把輸入分成幾個「行為一樣」的區間，每區取一個代表值測。
#               例如數量 1、5、100 行為都一樣，測一個就夠。
#
#   邊界值分析：區間的交界處最容易寫錯，所以每個邊界的「前後」都要測。
#               例如規則是「數量必須大於 0」，那就要測 -1、0、1。
#
# cart.add 的規則：qty <= 0 要丟例外，qty >= 1 才合法。
# 邊界在 0 和 1 之間。
# =====================================================================
@pytest.mark.parametrize("qty", [-5, -1, 0])
def test_invalid_quantity_raises(qty):
    cart = ShoppingCart()
    with pytest.raises(ValueError):
        cart.add("蘋果", price=30, qty=qty)


@pytest.mark.parametrize("qty, expected_total", [
    (1, 30),        # 邊界：最小的合法值
    (2, 60),
    (100, 3000),    # 很大的值
])
def test_valid_quantity_total(qty, expected_total):
    cart = ShoppingCart()
    cart.add("蘋果", price=30, qty=qty)
    assert cart.total() == expected_total


# =====================================================================
# 【小技巧】用 ids 讓報告好讀
#
# 預設的測試名稱是參數值拼起來的，有時候看不懂。
# 可以自己給每一組取名字。
# =====================================================================
@pytest.mark.parametrize("code, expected_price", [
    ("SAVE10", 90),
    ("SAVE20", 80),
    ("HALF", 50),
], ids=["10_percent_off", "20_percent_off", "half_price"])
def test_discount_codes_with_ids(code, expected_price):
    cart = ShoppingCart()
    cart.add("蘋果", price=100)
    assert cart.total(code) == expected_price


# 跑 -v 會看到 test_discount_codes_with_ids[10_percent_off] 這種名字，比 [SAVE10-90] 好讀


# =====================================================================
# 💡 試試看
#
# 1. 跑 pytest -v step5_parametrize.py，數一數總共幾個測試。
#    （檔案裡只有 7 個函式，但測試數量會超過 7）
#
# 2. 無效折扣碼會丟 ValueError。自己加一組 parametrize 測它：
#    測 "INVALID"、""、None 三種。
#    注意：None 是合法的（代表不用折扣碼），所以不該丟例外。
#    這題在考你有沒有看清楚規格。
#
# 3. 把 test_valid_quantity_total 的 (1, 30) 拿掉，
#    然後去改 cart.py 把 `if qty <= 0` 改成 `if qty <= 1`。
#    你的測試抓得到這個 bug 嗎？
#    （抓不到 —— 這就是為什麼一定要測邊界）
# =====================================================================
