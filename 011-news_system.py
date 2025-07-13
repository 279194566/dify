import json
from datetime import datetime, timezone, timedelta

def main(arg1: str) -> dict:
    try:
        # 如果已经是 dict 或 list，直接用，不再 loads
        if isinstance(arg1, (dict, list)):
            parsed_data = arg1
        else:
            parsed_data = json.loads(arg1)

        # 后续逻辑保持不变
        if isinstance(parsed_data, dict) and "arg1" in parsed_data:
            data = parsed_data["arg1"]
        else:
            data = parsed_data

        articles = []
        if isinstance(data, list):
            for item in data:
                articles.extend(item.get("articles", []))
        elif isinstance(data, dict):
            articles = data.get("articles", [])

        table = []

        # 添加表头
        table.append(["标题", "热门评分", "新闻链接-手机端", "新闻链接-PC端", "更新时间"])

        for item in articles:
            title = item.get('title', '')
            hot_score = item.get('hot_score', '')
            mobile_link = item.get('links', {}).get('mobile', '')
            pc_link = item.get('links', {}).get('pc', '')
            update_time_raw = item.get('metadata', {}).get('update_time', '')

            update_time = ''
            if update_time_raw:
                try:
                    # 先尝试按 ISO8601 带毫秒Z格式解析
                    dt_utc = datetime.strptime(update_time_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
                    dt_utc = dt_utc.replace(tzinfo=timezone.utc)
                    # 转换为上海时间（UTC+8）
                    shanghai_tz = timezone(timedelta(hours=8))
                    dt_shanghai = dt_utc.astimezone(shanghai_tz)
                    update_time = dt_shanghai.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    try:
                        # 不带毫秒的ISO8601格式
                        dt_utc = datetime.strptime(update_time_raw, "%Y-%m-%dT%H:%M:%SZ")
                        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
                        shanghai_tz = timezone(timedelta(hours=8))
                        dt_shanghai = dt_utc.astimezone(shanghai_tz)
                        update_time = dt_shanghai.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        try:
                            # 如果是时间戳（秒级或毫秒级）
                            ts = int(update_time_raw)
                            if len(str(update_time_raw)) == 13:
                                ts = ts / 1000
                            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                            dt_shanghai = dt.astimezone(timezone(timedelta(hours=8)))
                            update_time = dt_shanghai.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception:
                            # 直接使用原始字符串
                            update_time = str(update_time_raw)

            table.append([title, hot_score, mobile_link, pc_link, update_time])

        return {
            "result": str(table).replace("'", '"')
        }

    except Exception as e:
        return {
            "result": [["错误", f"{type(e).__name__}: {e}"]]
        }
