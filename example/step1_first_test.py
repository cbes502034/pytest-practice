"""
=====================================================================
 第 1 步：一個測試長什麼樣
=====================================================================

跑法：
    cd example
    pytest step1_first_test.py

這一步只有三個規則要記：
  1. 檔名要以 test_ 開頭或結尾   → 這個檔案叫 step1_...，所以要指定檔名才跑得到
  2. 函式名稱要以 test_ 開頭     → pytest 靠這個找測試
  3. 用 assert 寫你的期望

就這樣。沒有 class、沒有繼承、沒有 setUp。
"""

from cart import ShoppingCart


def test_new_cart_is_empty():
    cart = ShoppingCart()
    assert cart.count() == 0


def test_one_item_after_add():
    cart = ShoppingCart()
    cart.add("蘋果", price=30)
    assert cart.count() == 1


def test_total_is_price_times_qty():
    cart = ShoppingCart()
    cart.add("蘋果", price=30, qty=3)
    assert cart.total() == 100


# =====================================================================
# 💡 試試看
#
# 1. 跑 pytest step1_first_test.py
#    應該看到 3 passed
#
# 2. 加上 -v 再跑一次：pytest -v step1_first_test.py
#    這次會列出每一個測試的名字。看得出來測試名稱取得好有多重要嗎？
#
# 3. 把最後一個測試的 90 改成 100，跑跑看會怎樣。
#    （下一步就是在講這個）
# =====================================================================
