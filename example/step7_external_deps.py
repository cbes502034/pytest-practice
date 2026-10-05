"""
=====================================================================
 第 7 步：測外部依賴 —— 不要真的去扣錢
=====================================================================

跑法：
    pytest -v step7_external_deps.py

⭐ 這一步最接近真實工作。
"""

import pytest

from cart import ShoppingCart, PaymentFailed


# =====================================================================
# 【問題】checkout() 會呼叫金流扣款
#
# 如果測試直接打真實金流：
#   - 真的會扣到錢
#   - 沒網路就不能跑
#   - 外部服務掛了，你的測試跟著紅
#   - 你沒辦法叫金流「回傳失敗」給你測異常流程  ← 這點最致命
#
# 解法：塞一個「假的金流」進去。
# =====================================================================


# ---------------------------------------------------------------------
# cart.checkout(payment_client) 的 payment_client 是傳進來的，
# 所以我們可以自己做一個假的。
#
# 它只要有 charge(amount) 方法就行 —— Python 不檢查型別，
# 長得像就可以用（這叫 duck typing）。
# ---------------------------------------------------------------------
class SuccessfulPayment:
    def __init__(self):
        self.charged_amounts = []           # 記錄被呼叫的情況

    def charge(self, amount):
        self.charged_amounts.append(amount)
        return {"success": True, "transaction_id": "TX123"}


class FailingPayment:
    def charge(self, amount):
        return {"success": False, "message": "餘額不足"}


# =====================================================================
# 測試 1：正常結帳
# =====================================================================
def test_checkout_success():
    cart = ShoppingCart()
    cart.add("蘋果", price=100, qty=2)

    payment = SuccessfulPayment()
    result = cart.checkout(payment)

    assert result["paid"] == 200
    assert result["transaction_id"] == "TX123"


# =====================================================================
# 測試 2：⭐ 驗證「真的有呼叫金流，而且金額正確」
#
# 這點很重要。上面那個測試只檢查了回傳值，
# 但如果 checkout 根本沒呼叫 charge，直接回傳假資料呢？測不出來。
#
# 所以要檢查「互動」，不只檢查「結果」。
# =====================================================================
def test_checkout_sends_correct_amount():
    cart = ShoppingCart()
    cart.add("蘋果", price=100, qty=2)

    payment = SuccessfulPayment()
    cart.checkout(payment)

    assert payment.charged_amounts == [200]       # 被呼叫一次，金額是 200


def test_charge_uses_discounted_amount():
    cart = ShoppingCart()
    cart.add("蘋果", price=100, qty=2)

    payment = SuccessfulPayment()
    cart.checkout(payment, discount_code="SAVE10")

    assert payment.charged_amounts == [180]       # 200 打九折


# =====================================================================
# 測試 3：⭐ 異常流程 —— 這是假金流最大的價值
#
# 真實金流你沒辦法叫它「失敗給我看」，但假的可以。
# =====================================================================
def test_payment_failure_raises():
    cart = ShoppingCart()
    cart.add("蘋果", price=100)

    with pytest.raises(PaymentFailed, match="餘額不足"):
        cart.checkout(FailingPayment())


def test_cart_kept_when_payment_fails():
    """這是真正重要的一條：付款失敗，東西要還在，使用者才能重試。"""
    cart = ShoppingCart()
    cart.add("蘋果", price=100)

    with pytest.raises(PaymentFailed):
        cart.checkout(FailingPayment())

    assert cart.count() == 1          # 商品還在


def test_cart_cleared_after_payment():
    cart = ShoppingCart()
    cart.add("蘋果", price=100)

    cart.checkout(SuccessfulPayment())

    assert cart.count() == 0


# =====================================================================
# 【另一種做法】monkeypatch
#
# 上面是「依賴注入」—— 因為 cart.checkout 設計成可以把金流傳進去。
# 如果程式沒這樣設計（例如直接在函式裡 import 外部模組），
# 就要用 monkeypatch 把東西換掉。
#
# pytest 內建 monkeypatch，測試結束會自動還原。
# =====================================================================
def test_replace_method_with_monkeypatch(monkeypatch):
    cart = ShoppingCart()
    cart.add("蘋果", price=100)

    # 把 cart.total 換成永遠回 999
    monkeypatch.setattr(cart, "total", lambda discount_code=None: 999)

    payment = SuccessfulPayment()
    result = cart.checkout(payment)

    assert result["paid"] == 999


# =====================================================================
# 💡 想一想
#
# 1. 依賴注入 vs monkeypatch，哪個好？
#
#    依賴注入：需要程式本來就設計得好，但測試穩定、意圖清楚
#    monkeypatch：什麼都能換，但綁死內部實作 —— 重構一下測試就壞
#
#    結論：能用注入就用注入。
#    有一句話可以記：「好測的程式，通常也是設計得好的程式。」
#
# 2. test_cart_kept_when_payment_fails 這種測試叫什麼？
#    它測的不是「正常功能」，是「出錯之後系統有沒有保持在合理狀態」。
#    這類測試在真實專案裡往往比正常流程的測試更有價值。
# =====================================================================
