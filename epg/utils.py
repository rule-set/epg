from datetime import datetime, timedelta
import pytz


def add_stop_time_by_duration(programmes, format):
    for p in programmes:
        time_object = datetime.strptime(p["stop"], format)
        delta = timedelta(
            hours=time_object.hour,
            minutes=time_object.minute,
            seconds=time_object.second,
        )
        dt_object = datetime.strptime(p["start"], "%Y%m%d%H%M%S") + delta
        p["stop"] = dt_object.strftime("%Y%m%d%H%M%S")


def add_stop_time_by_second(programmes):
    for p in programmes:
        dt_object = datetime.strptime(p["start"], "%Y%m%d%H%M%S") + timedelta(
            seconds=int(p["stop"])
        )
        p["stop"] = dt_object.strftime("%Y%m%d%H%M%S")


def add_stop_time_to_info(programmes):
    sorted_programs = sorted(programmes, key=lambda x: x["start"])
    for i in range(len(sorted_programs) - 1):
        sorted_programs[i]["stop"] = sorted_programs[i + 1]["start"]
    if sorted_programs:
        sorted_programs[-1]["stop"] = sorted_programs[-1]["start"][:8] + "235959"


def time_to_seconds(time_str, fmt="%H:%M"):
    time_obj = datetime.strptime(time_str, fmt)
    hours = time_obj.hour
    minutes = time_obj.minute
    seconds = time_obj.second

    total_seconds = hours * 3600 + minutes * 60 + seconds

    return total_seconds


def convert_date_with_tz(date_string, format, from_tz):
    from_time = datetime.strptime(date_string, format)
    from_time = pytz.timezone(from_tz).localize(from_time)
    dt_object = from_time.astimezone(pytz.timezone("Asia/Shanghai"))

    return dt_object.strftime("%Y%m%d%H%M%S")


def convert_date_string(date_string, format, delta):
    dt_object = datetime.strptime(date_string, format) + timedelta(hours=delta)
    return dt_object.strftime("%Y%m%d%H%M%S")


def convert_timestamp(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    # + timedelta(hours=8)
    return dt_object.strftime("%Y%m%d%H%M%S")


def generate_ts_from_monday(begin_days=7, end_days=7):
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(tz)
    monday = now - timedelta(days=now.weekday())
    monday_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return [
        int((monday_start + timedelta(days=i)).timestamp()) for i in range(end_days + 1)
    ]


def generate_dates_from_monday(end_days=14, fmt="%Y%m%d"):
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(tz)
    monday = now - timedelta(days=now.weekday())
    monday_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return [
        (monday_start + timedelta(days=i)).strftime(fmt) for i in range(end_days + 1)
    ]


def generate_formatted_date(
    start_days_ago=7, end_days_in_future=7, fmt="%Y-%m-%d", tz="Asia/Shanghai"
):
    local_tz = pytz.timezone(tz)
    now = datetime.now(local_tz)

    start_date = now - timedelta(days=start_days_ago)
    end_date = now + timedelta(days=end_days_in_future)

    return start_date.strftime(fmt), end_date.strftime(fmt)


def generate_formatted_date_range(
    start_days_ago=7, end_days_in_future=7, fmt="%Y-%m-%d", tz="Asia/Shanghai"
):
    local_tz = pytz.timezone(tz)
    now = datetime.now(local_tz)
    start_date = now - timedelta(days=start_days_ago)
    end_date = now + timedelta(days=end_days_in_future)
    date_list = [
        (start_date + timedelta(days=x)).astimezone(local_tz).strftime(fmt)
        for x in range((end_date - start_date).days + 1)
    ]
    return date_list


def generate_timestamp_range(
    start_days_ago=7, end_days_in_future=7, tz="Asia/Shanghai"
):
    local_tz = pytz.timezone(tz)
    now = datetime.now(local_tz)
    start = now - timedelta(days=start_days_ago)
    start_ts = start.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    end = now + timedelta(days=end_days_in_future)
    end_ts = end.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    return start_ts, end_ts
