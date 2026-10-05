"""
XVR-lite —— 模擬資安監控平台（SOC）的一小段處理管線

    原始日誌 ──► parse_event ──► DetectionEngine ──► Alert ──► Responder ──► 防火牆
               ingest_batch     BruteForceRule                              (外部系統)
               (Unit 1-3)       (Unit 4-6)                    (Unit 7)

這是你要「測試」的程式。⚠️ 不要修改它。
⚠️ 裡面有一個刻意留下的 bug，Unit 2 會用到。
"""
import ipaddress
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field

VALID_ACTIONS = {"login_failed", "login_success", "conn_blocked", "conn_allowed"}
REQUIRED_FIELDS = ("ts", "src_ip", "action")
PRIVILEGED_USERS = {"admin", "root", "administrator"}


# =====================================================================
# 第一段：日誌解析（Unit 1、2、3）
# =====================================================================
class MalformedEvent(Exception):
    """日誌格式錯誤。"""


def parse_event(line):
    """
    把一行 JSON 日誌解析成標準格式的 dict。

    輸入範例：
        '{"ts": 1700000000, "src_ip": "45.67.89.10", "action": "login_failed",
          "user": "admin", "dst_port": 22}'

    必填欄位：ts、src_ip、action
    選填欄位：user、dst_port

    回傳的 dict：
        ts        -> float（秒）
        src_ip    -> str（原樣保留，支援 IPv4 / IPv6）
        action    -> str（原樣保留，不轉大小寫）
        user      -> str，沒有這個欄位時為 None
        dst_port  -> int，沒有這個欄位時為 None
                     ※ 有些設備會送字串 "443"，必須轉成整數 443

    格式錯誤時 raise MalformedEvent，訊息說明原因：
        不是 JSON           -> "非 JSON 格式"
        缺必填欄位          -> "缺少欄位: <欄位名>"
        ts 不是數字         -> "時間格式錯誤"
        src_ip 不合法       -> "IP 格式錯誤"
        action 不在清單內   -> "未知的 action: <值>"
        dst_port 不是數字   -> "port 格式錯誤"
        dst_port 不在 1~65535 -> "port 超出範圍"
    """
    try:
        raw = json.loads(line)
    except (json.JSONDecodeError, TypeError):
        raise MalformedEvent("非 JSON 格式")
    if not isinstance(raw, dict):
        raise MalformedEvent("非 JSON 格式")

    for name in REQUIRED_FIELDS:
        if name not in raw:
            raise MalformedEvent(f"缺少欄位: {name}")

    try:
        ts = float(raw["ts"])
    except (TypeError, ValueError):
        raise MalformedEvent("時間格式錯誤")

    src_ip = raw["src_ip"]
    try:
        if not isinstance(src_ip, str):
            raise ValueError
        ipaddress.ip_address(src_ip)
    except ValueError:
        raise MalformedEvent("IP 格式錯誤")

    action = raw["action"]
    if action not in VALID_ACTIONS:
        raise MalformedEvent(f"未知的 action: {action}")

    port = raw.get("dst_port")
    if port is not None:
        if isinstance(port, str) and not port.isdigit():
            raise MalformedEvent("port 格式錯誤")
        if not 1 <= int(port) <= 65535:
            raise MalformedEvent("port 超出範圍")

    return {
        "ts": ts,
        "src_ip": src_ip,
        "action": action,
        "user": raw.get("user"),
        "dst_port": port,
    }


@dataclass
class IngestResult:
    events: list = field(default_factory=list)   # 解析成功的事件
    rejected: int = 0                            # 被拒絕的行數
    reasons: list = field(default_factory=list)  # 每一行被拒絕的原因


def ingest_batch(lines):
    """
    批次匯入多行日誌。

    - 格式錯誤的行：跳過，記錄在 reasons，格式為 "第 N 行: <原因>"（N 從 1 開始）
    - 空白行：直接略過，不算 rejected
    - 不管內容多糟，這個函式本身都不可以丟例外 —— 一行壞資料不能讓整批停擺
    """
    result = IngestResult()
    for lineno, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            result.events.append(parse_event(line))
        except MalformedEvent as exc:
            result.reasons.append(f"第 {lineno} 行: {exc}")
    result.rejected = len(result.reasons)
    return result


# =====================================================================
# 第二段：偵測規則（Unit 4、5、6）
# =====================================================================
@dataclass
class Alert:
    rule: str          # 規則名稱
    src_ip: str        # 攻擊來源
    severity: str      # "high" / "medium"
    mitre: str         # MITRE ATT&CK 技術編號
    ts: float          # 觸發時間
    count: int         # 時間窗內的失敗次數
    user: str = None   # 觸發當下的帳號


class BruteForceRule:
    """
    暴力破解偵測（MITRE ATT&CK T1110）

    規則：
      - 同一個 src_ip，在 window 秒內 login_failed 達到 threshold 次 → 產生一則告警
      - 時間窗包含邊界：最新事件與最舊事件相差「剛好 window 秒」仍算在窗內
      - 只看 login_failed；其他 action 不計數
      - 該 IP 一旦 login_success，失敗紀錄清空
      - 同一個 IP 告警後，window 秒內不重複告警（避免洗版）
      - 嚴重度：觸發當下的帳號是特權帳號（admin / root / administrator，不分大小寫）→ "high"
                其他 → "medium"
    """

    name = "brute_force"
    mitre = "T1110"

    def __init__(self, threshold=5, window=300):
        self.threshold = threshold
        self.window = window
        self._fails = defaultdict(deque)   # ip -> 失敗時間序列
        self._last_alert = {}              # ip -> 上次告警時間

    def evaluate(self, event):
        ip = event["src_ip"]
        action = event["action"]

        if action == "login_success":
            self._fails.pop(ip, None)
            return None
        if action != "login_failed":
            return None

        now = event["ts"]
        fails = self._fails[ip]
        fails.append(now)
        while fails and now - fails[0] > self.window:
            fails.popleft()

        if len(fails) < self.threshold:
            return None

        last = self._last_alert.get(ip)
        if last is not None and now - last <= self.window:
            return None
        self._last_alert[ip] = now

        user = event.get("user")
        severity = "high" if (user or "").lower() in PRIVILEGED_USERS else "medium"
        return Alert(self.name, ip, severity, self.mitre, now, len(fails), user)

    def reset(self):
        self._fails.clear()
        self._last_alert.clear()


class DetectionEngine:
    """把事件依序餵給每一條規則，收集告警。"""

    def __init__(self, rules=None):
        self.rules = rules if rules is not None else [BruteForceRule()]
        self.alerts = []
        self.events_seen = 0

    def feed(self, event):
        self.events_seen += 1
        new_alerts = []
        for rule in self.rules:
            alert = rule.evaluate(event)
            if alert is not None:
                new_alerts.append(alert)
        self.alerts.extend(new_alerts)
        return new_alerts

    def feed_many(self, events):
        produced = []
        for event in events:
            produced.extend(self.feed(event))
        return produced

    def reset(self):
        self.alerts.clear()
        self.events_seen = 0
        for rule in self.rules:
            rule.reset()


# =====================================================================
# 第三段：自動回應（Unit 7）
# =====================================================================
class FirewallError(Exception):
    """防火牆 API 呼叫失敗（逾時、連線中斷……）。"""


class FirewallClient:
    """真實防火牆的 API 客戶端。⚠️ 測試中絕對不可以呼叫它。"""

    def block(self, ip, reason):
        raise RuntimeError("測試不該呼叫真實防火牆！請注入一個假的 firewall。")


class Responder:
    """
    依告警決定要不要自動封鎖。「判斷」在這裡，「執行」交給防火牆。

    handle(alert) 回傳下列其中一個字串：

      "skipped"      src_ip 在 allowlist，或是內網 IP（10.x / 172.16-31.x / 192.168.x）
                     → 絕對不封鎖，也不可以呼叫 firewall
      "notified"     嚴重度不是 high → 只通知分析師，不呼叫 firewall
      "blocked"      嚴重度 high → 呼叫 firewall.block(ip, reason="<規則>:<MITRE編號>")，成功
      "block_failed" 呼叫 firewall 時發生 FirewallError，或回傳 {"ok": False}
                     → 不可以讓例外往外丟；把告警放進 pending_review 讓人工處理
    """

    def __init__(self, firewall, allowlist=()):
        self.firewall = firewall
        self.allowlist = set(allowlist)
        self.pending_review = []

    def handle(self, alert):
        ip = alert.src_ip
        if ip in self.allowlist or ipaddress.ip_address(ip).is_private:
            return "skipped"
        if alert.severity != "high":
            return "notified"
        try:
            response = self.firewall.block(ip, reason=f"{alert.rule}:{alert.mitre}")
        except FirewallError:
            self.pending_review.append(alert)
            return "block_failed"
        if not response.get("ok"):
            self.pending_review.append(alert)
            return "block_failed"
        return "blocked"
