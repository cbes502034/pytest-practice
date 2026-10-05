"""
=====================================================================
 第 4 步：fixture —— 解決「每個測試都要重複做前置動作」
=====================================================================

跑法：
    pytest -v -s step4_fixture.py        ← 加 -s 才看得到 print

先看問題，再看解法。
"""

import pytest

from cart import ShoppingCart


# =====================================================================
# 【問題】每個測試開頭都在做一樣的事
# =====================================================================
def test_old_total():
    cart = ShoppingCart()           # ← 重複
    cart.add("蘋果", price=30, qty=2)  # ← 重複
    cart.add("香蕉", price=20, qty=1)  # ← 重複
    assert cart.total() == 80


def test_old_item_count():
    cart = ShoppingCart()           # ← 又來一次
    cart.add("蘋果", price=30, qty=2)
    cart.add("香蕉", price=20, qty=1)
    assert cart.count() == 2


def test_old_discount():
    cart = ShoppingCart()           # ← 第三次了
    cart.add("蘋果", price=30, qty=2)
    cart.add("香蕉", price=20, qty=1)
    assert cart.total("SAVE10") == 72


# 三個測試，同樣的四行前置寫了三遍。
# 如果商品價格改了，要改三個地方。這就是 fixture 要解決的事。


# =====================================================================
# 【解法】fixture
#
# @pytest.fixture 把一個函式變成「可以被測試要求的資源」。
# 測試只要把 fixture 的名字寫進參數，pytest 就會自動呼叫它、把結果傳進來。
# =====================================================================
@pytest.fixture
def filled_cart():
    """一個已經放了蘋果 x2、香蕉 x1 的購物車。"""
    print("\n    [fixture] 建立購物車")
    cart = ShoppingCart()
    cart.add("蘋果", price=30, qty=2)
    cart.add("香蕉", price=20, qty=1)
    return cart


def test_new_total(filled_cart):          # ← 名字要跟 fixture 一樣
    assert filled_cart.total() == 80


def test_new_item_count(filled_cart):
    assert filled_cart.count() == 2


def test_new_discount(filled_cart):
    assert filled_cart.total("SAVE10") == 72


# =====================================================================
# 【重點】每個測試拿到的是「全新的」購物車
#
# 跑 pytest -v -s 會看到 [fixture] 建立購物車 印了很多次 ——
# 每個測試各一次。這叫做 scope="function"，是預設值。
#
# 為什麼重要？看下面這兩個測試：
# =====================================================================
def test_add_item_in_this_test(filled_cart):
    filled_cart.add("西瓜", price=200)
    assert filled_cart.count() == 3


def test_still_get_clean_cart(filled_cart):
    # 上一個測試加了西瓜，但我這裡還是只有 2 種
    # 因為 fixture 每次都重新建立
    assert filled_cart.count() == 2


# =====================================================================
# 【進階】yield：測試跑完之後要收尾
#
# 上面的 fixture 用 return。如果需要「測試結束後做清理」，
# 就把 return 換成 yield —— yield 之前是準備，之後是清理。
#
# 即使測試失敗了，yield 之後的程式碼還是會執行。
# =====================================================================
@pytest.fixture
def cart_with_teardown():
    print("\n    [setup] 開始")
    cart = ShoppingCart()
    cart.add("蘋果", price=30)

    yield cart                      # ← 測試在這裡執行

    print("    [teardown] 收尾")    # ← 測試跑完才執行
    cart._items.clear()


def test_uses_teardown_fixture(cart_with_teardown):
    assert cart_with_teardown.count() == 1


# =====================================================================
# 💡 試試看
#
# 1. 跑 pytest -v -s step4_fixture.py，數一數 [fixture] 建立購物車 印了幾次。
#
# 2. 把 @pytest.fixture 改成 @pytest.fixture(scope="module")，再跑一次。
#    - [fixture] 只會印一次
#    - 但 test_still_get_clean_cart 會失敗！
#    這就是 scope 的意義：共用資源比較快，但測試之間會互相影響。
#    改完記得改回來。
#
# 3. 把 test_uses_teardown_fixture 裡的 assert 改成錯的，跑一次。
#    觀察 [teardown] 收尾 有沒有印出來。（會。這就是 yield 的價值）
#
#
# 📌 scope 一共五種，由短到長：
#    function（預設）→ class → module → package → session
#
#    實務上什麼時候用 session？
#    起 Docker 容器（Elasticsearch、MySQL）的時候 ——
#    每個測試都重起一次容器會慢到不能用。
# =====================================================================
