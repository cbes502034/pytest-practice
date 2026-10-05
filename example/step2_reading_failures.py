"""
=====================================================================
 第 2 步：失敗的時候 pytest 會告訴你什麼
=====================================================================

跑法：
    pytest step2_reading_failures.py

這個檔案裡有兩個測試是「故意寫錯的」，會失敗。
重點不是修好它們，是**看清楚 pytest 印出什麼**。

pytest 有一個叫 assertion rewriting 的功能：
它會把你的 assert 運算式拆開，告訴你左邊是什麼、右邊是什麼。
這是它比 unittest 好用的地方之一 —— 不用背 assertEqual 也看得懂哪裡錯。
"""

from cart import ShoppingCart


def test_this_passes():
    cart = ShoppingCart()
    cart.add("蘋果", price=30, qty=2)
    assert cart.total() == 60


def test_wrong_number_on_purpose():
    cart = ShoppingCart()
    cart.add("蘋果", price=30, qty=2)
    assert cart.total() == 100      # ← 實際是 60


def test_wrong_list_on_purpose():
    cart = ShoppingCart()
    cart.add("蘋果", price=30)
    cart.add("香蕉", price=20)
    # 故意拿一個不存在的方法來比，示範比較複雜的失敗訊息
    assert [cart.count(), cart.total()] == [3, 999]


# =====================================================================
# 💡 看輸出的時候注意這幾件事
#
# 1. 失敗的測試前面有 F，通過的有 .
#
# 2. 失敗區塊會印出：
#       >       assert cart.total() == 100
#       E       assert 60.0 == 100
#       E        +  where 60.0 = <bound method ShoppingCart.total ...>()
#    它把 cart.total() 算出來的值（60.0）直接寫給你看了。
#
# 3. 最下面會有一行總結：
#       =========== 1 passed, 2 failed in 0.03s ===========
#
# 4. 試試 pytest -x step2_reading_failures.py
#    -x 的意思是「第一個失敗就停下來」，debug 的時候很好用。
# =====================================================================
