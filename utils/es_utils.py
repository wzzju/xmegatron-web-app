import traceback
from datetime import datetime, timedelta

import pytz
from elasticsearch import Elasticsearch

DATE_FMT = "%a %b %-d %H:%M:%S %Y %z"
TIME_ZONE = "Asia/Shanghai"
INDEX_NAME = "quality_monitor"
ES_ADDR = ["http://172.219.129.21:8901"]
ES_USR = "usr"
ES_PWD = "123"
ES_CLIENT = None


def get_or_connect_es(addr=ES_ADDR, usr=ES_USR, pwd=ES_PWD):
    global ES_CLIENT
    if ES_CLIENT is None:
        es = Elasticsearch(addr, basic_auth=(usr, pwd))

        if es.ping():
            print("Successfully connected to Elasticsearch!")
        else:
            raise Exception("Could not connect to Elasticsearch.")
        ES_CLIENT = es

    return ES_CLIENT


def _get_date_obj(date_str):
    formats = ["%a %b %d %H:%M:%S %Y %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
    for fmt in formats:
        try:
            date = datetime.strptime(date_str, fmt)
            return True, date
        except ValueError:
            continue
    return False, None


def _format_commit(commit):
    data = commit.split("@")
    assert len(data) == 2, f"bad commit: {commit}"
    branch, cid = data[0], data[1]
    if len(cid) > 7:
        cid = cid[:7]
    return f"{branch}@{cid}"


def search_data(start_date=None, end_date=None, index_name=INDEX_NAME, es=ES_CLIENT):
    if end_date is None:
        end_date = datetime.now(pytz.timezone(TIME_ZONE)).strftime(DATE_FMT)
    if start_date is None:
        start_date = (datetime.now(pytz.timezone(TIME_ZONE)) - timedelta(days=30)).strftime(
            DATE_FMT
        )

    query_conditions = {
        "query": {
            "range": {
                "commit_date": {
                    "gte": start_date,
                    "lte": end_date,
                }
            }
        },
        "sort": [{"commit_date": {"order": "asc"}}],  # 按时间升序排序
        "size": 1000,  # 最多返回1000个查询结果
    }

    dense_date, dense_acc, dense_perf, dense_meta = [], [], [], []
    moe_date, moe_acc, moe_perf, moe_meta = [], [], [], []
    try:
        response = es.search(index=index_name, body=query_conditions)
        for hit in response['hits']['hits']:
            doc = hit['_source']
            model_type = doc['model_type']
            date = doc['commit_date']
            success, date_obj = _get_date_obj(date)
            if success:
                date = date_obj
            acc = doc['acc']
            perf = doc['perf']
            trigger_repo = doc['trigger_repo']
            xmlir_commit = _format_commit(doc['xmlir_commit'])
            llm_commit = _format_commit(doc['llm_commit'])
            mextension_commit = _format_commit(doc['mextension_commit'])
            mcore_commit = _format_commit(doc['mcore_commit'])
            meta_info = (
                f"<b>Trigger Repo</b>: {trigger_repo}<br>"
                + f"<b>XMLIR Commit</b>: {xmlir_commit}<br>"
                + f"<b>LLM Commit</b>: {llm_commit}<br>"
                + f"<b>MExtension Commit</b>: {mextension_commit}<br>"
                + f"<b>MCore Commit</b>: {mcore_commit}"
            )

            if model_type == "Dense":
                dense_date.append(date)
                dense_acc.append(acc)
                dense_perf.append(perf)
                dense_meta.append(meta_info)
            elif model_type == "MoE":
                moe_date.append(date)
                moe_acc.append(acc)
                moe_perf.append(perf)
                moe_meta.append(meta_info)
    except Exception:
        traceback.print_stack()

    return dense_date, moe_date, dense_meta, moe_meta, dense_acc, moe_acc, dense_perf, moe_perf
