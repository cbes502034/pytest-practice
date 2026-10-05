"""
=====================================================================
 第 6 步：marker —— 幫測試貼標籤，可以挑著跑
=====================================================================

跑法：
    pytest -v step6_marker.py
    pytest -v -m "not slow" step6_marker.py
"""

import sys

import pytest

from cart import ShoppingCart


# =====================================================================
# 【問題】測試套件越來越大，有些很慢
#
# 你不會想每改一行就等五分鐘。
# 但也不能不跑 —— 所以需要「分類」。
# =====================================================================


# ---------------------------------------------------------------------
# 自訂 marker：先在 conftest.py 註冊（這個資料夾已經有了），
# 然後用 @pytest.mark.標籤名 貼上去。
# ---------------------------------------------------------------------
@pytest.mark.slow
def test_add_ten_thousand_items():
    cart = ShoppingCart()
    for i in range(10000):
        cart.add(f"商品{i}", price=1)
    assert cart.count() == 10000


def test_fast():
    cart = ShoppingCart()
    cart.add("蘋果", price=30)
    assert cart.count() == 1


# 現在你可以：
#     pytest -m "slow"        只跑慢的
#     pytest -m "not slow"    跳過慢的      ← 開發時都用這個
#
# 實務上 CI 就是這樣分層：
#     開 PR 時      → pytest -m "not slow"     幾分鐘內要有結果
#     半夜定時跑    → pytest                   全部跑完


# =====================================================================
# 【內建 marker 1】skip —— 這個測試不要跑
# =====================================================================
@pytest.mark.skip(reason="這個功能還沒做")
def test_not_implemented_yet():
    cart = ShoppingCart()
    cart.remove("蘋果")      # ShoppingCart 根本沒有 remove 方法


@pytest.mark.skipif(sys.platform == "win32", reason="這個只在 Linux 有意義")
def test_linux_only():
    assert sys.platform != "win32"


# =====================================================================
# 【內建 marker 2】xfail —— 這個測試要跑，而且預期它會失敗
#
# ⭐ skip 和 xfail 的差別很重要，面試會問：
#
#     skip  = 不跑。這個測試被完全忽略。
#     xfail = 要跑，但失敗不算錯。
#
# 什麼時候用 xfail？「已知的缺陷，還沒時間修」。
#
# 好處：萬一哪天它意外通過了，pytest 會報 XPASS，
#       提醒你「bug 可能被修好了，該把標記拿掉」。
#       用 skip 的話你永遠不會知道。
# =====================================================================

# ShoppingCart 有個小問題：同樣商品再加一次，會用「新的價格」覆蓋舊的。
# 下面這個測試描述的是「比較合理的行為」，所以現在會失敗。
@pytest.mark.xfail(reason="已知行為：重複加入同一商品會用新價格覆蓋舊價格")
def test_readd_keeps_original_price():
    cart = ShoppingCart()
    cart.add("蘋果", price=30, qty=1)
    cart.add("蘋果", price=50, qty=1)      # 價格變了
    # 期望：2 顆都算 30 元 = 60
    # 實際：2 顆都算 50 元 = 100
    assert cart.total() == 60


# =====================================================================
# 【組合技】parametrize 裡單獨標記某一組
# =====================================================================
@pytest.mark.parametrize("code, expected_price", [
    ("SAVE10", 90),
    ("SAVE20", 80),
    pytest.param("BLACKFRIDAY", 10, marks=pytest.mark.xfail(reason="這個折扣碼還沒上線")),
])
def test_discount_codes_with_unreleased(code, expected_price):
    cart = ShoppingCart()
    cart.add("蘋果", price=100)
    assert cart.total(code) == expected_price


# =====================================================================
# 💡 試試看
#
# 1. pytest -v step6_marker.py
#    看 s（skipped）、x（xfailed）各出現在哪裡
#
# 2. pytest -v -m "not slow" step6_marker.py
#    最後會顯示 1 deselected
#
# 3. 把 test_readd_keeps_original_price 的期望值從 60 改成 100，再跑一次。
#    它會變成 XPASS —— pytest 在跟你說「你說會失敗的測試居然過了」。
#
#
# 📌 輸出符號對照
#     .  通過       F  失敗       E  錯誤（測試本身炸了）
#     s  跳過       x  預期失敗   X  預期失敗但居然過了（XPASS）
# =====================================================================
