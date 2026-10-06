"""
=====================================================================
 第 3 步：怎麼測「應該要出錯」的情況
=====================================================================

跑法：
    pytest -v step3_exceptions.py

到目前為止我們都在測「正常情況」。
但好的測試要測「壞掉的情況」—— 而且壞得對不對。

cart.py 裡寫了兩條規則：
    價格為負 → raise ValueError("價格不可為負數")
    數量 <= 0 → raise ValueError("數量必須大於 0")

怎麼測「它應該要丟例外」？用 pytest.raises。
"""

import pytest

from cart import ShoppingCart


# ---------------------------------------------------------------------
# 錯誤示範：這樣寫是沒用的
# ---------------------------------------------------------------------
def test_bad_example_direct_call():
    cart = ShoppingCart()
    # 如果你直接這樣寫，例外會往外炸，測試會「錯誤」而不是「通過」
    #     cart.add("蘋果", price=-1)
    # 所以要用 with pytest.raises(...) 把它包起來
    pass


# ---------------------------------------------------------------------
# 正確做法
# ---------------------------------------------------------------------
def test_negative_price_raises():
    cart = ShoppingCart()
    with pytest.raises(ValueError):
        cart.add("蘋果", price=-1)


def test_zero_quantity_raises():
    cart = ShoppingCart()
    with pytest.raises(ValueError):
        cart.add("蘋果", price=30, qty=0)


# ---------------------------------------------------------------------
# 更進一步：連「錯誤訊息對不對」都檢查
#
# match 吃的是正規表示式，會對例外訊息做搜尋。
# 為什麼要檢查訊息？因為兩條規則都丟 ValueError，
# 如果不檢查訊息，你分不出來是哪一條被觸發的。
# ---------------------------------------------------------------------
def test_negative_price_error_message():
    cart = ShoppingCart()
    with pytest.raises(KeyError, match="價格"):
        cart.add("蘋果", price=-1)


def test_zero_quantity_error_message():
    cart = ShoppingCart()
    with pytest.raises(KeyError, match="數量"):
        cart.add("蘋果", price=30, qty=0)


# ---------------------------------------------------------------------
# 想看例外物件本身的話，用 as
# ---------------------------------------------------------------------
def test_inspect_exception_object():
    cart = ShoppingCart()
    with pytest.raises(KeyError) as exc_info:
        cart.add("蘋果", price=-1)

    assert "價格不可為負數" in str(exc_info.value)


# =====================================================================
# 💡 試試看
#
# 1. 把 match="價格" 改成 match="數量"，跑跑看。
#    失敗訊息會告訴你「訊息沒有符合這個 pattern」。
#
# 2. 把 pytest.raises(ValueError) 改成 pytest.raises(KeyError)。
#    會發生什麼事？（答：ValueError 會往外炸，測試變成 FAILED）
# =====================================================================
