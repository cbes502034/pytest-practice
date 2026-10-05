"""
conftest.py —— pytest 會自動載入這個檔案，不需要 import。

目前只用來註冊自訂 marker。
如果沒註冊，用 @pytest.mark.slow 的時候 pytest 會跳警告。
"""


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: 跑比較久的測試，開發時可以跳過")
