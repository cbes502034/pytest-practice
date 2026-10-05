"""
這是「被測試的程式」。從頭到尾都不會改它。

一個很單純的購物車：加商品、算總價、套折扣碼、結帳。
刻意寫得簡單，因為重點是學 pytest，不是學購物車。
"""


class PaymentFailed(Exception):
    """金流扣款失敗。"""


class ShoppingCart:
    # 折扣碼：代號 -> 折扣比例（0.9 = 打九折）
    DISCOUNTS = {
        "SAVE10": 0.9,
        "SAVE20": 0.8,
        "HALF": 0.5,
    }

    def __init__(self):
        self._items = {}        # name -> (price, qty)

    def add(self, name, price, qty=1):
        """加商品進購物車。同樣商品會累加數量。"""
        if price < 0:
            raise ValueError("價格不可為負數")
        if qty <= 0:
            raise ValueError("數量必須大於 0")

        if name in self._items:
            old_price, old_qty = self._items[name]
            self._items[name] = (price, old_qty + qty)
        else:
            self._items[name] = (price, qty)

    def count(self):
        """購物車裡有幾種商品。"""
        return len(self._items)

    def total(self, discount_code=None):
        """算總價。可以帶折扣碼。"""
        amount = sum(price * qty for price, qty in self._items.values())

        if discount_code is not None:
            if discount_code not in self.DISCOUNTS:
                raise ValueError(f"無效的折扣碼：{discount_code}")
            amount *= self.DISCOUNTS[discount_code]

        return amount

    def checkout(self, payment_client, discount_code=None):
        """
        結帳。會呼叫外部金流。

        payment_client 是傳進來的（依賴注入），
        所以測試的時候可以塞一個假的進來，不用真的扣錢。
        """
        amount = self.total(discount_code)
        result = payment_client.charge(amount)

        if not result.get("success"):
            raise PaymentFailed(result.get("message", "扣款失敗"))

        self._items.clear()
        return {"paid": amount, "transaction_id": result["transaction_id"]}
