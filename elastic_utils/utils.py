import traceback
from datetime import datetime, timedelta

import pytz
from elasticsearch import Elasticsearch

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
    try:
        date = datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y %z")
        return True, date
    except ValueError:
        return False, None


def search_data(start_date=None, end_date=None, index_name=INDEX_NAME, es=ES_CLIENT):
    if end_date is None:
        end_date = datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%a %b %-d %H:%M:%S %Y %z")
    if start_date is None:
        start_date = (datetime.now(pytz.timezone('Asia/Shanghai')) - timedelta(days=30)).strftime(
            "%a %b %-d %H:%M:%S %Y %z"
        )

    query_conditions = {
        "query": {
            "range": {
                "created_at": {
                    "gte": start_date,
                    "lte": end_date,
                }
            }
        },
        "sort": [{"created_at": {"order": "asc"}}],  # 按时间升序排序
        "size": 1000,  # 最多返回1000个查询结果
    }

    dense_date, dense_acc, dense_perf, dense_commit = [], [], [], []
    moe_date, moe_acc, moe_perf, moe_commit = [], [], [], []
    try:
        response = es.search(index=index_name, body=query_conditions)
        for hit in response['hits']['hits']:
            doc = hit['_source']
            model_type = doc['model_type']
            date = doc['created_at']
            success, date_obj = _get_date_obj(date)
            if success:
                date = date_obj
            acc = doc['acc']
            perf = doc['perf']
            commit_id = doc['commit_id']
            if len(commit_id) > 8:
                commit_id = commit_id[:8]

            if model_type == "Dense":
                dense_date.append(date)
                dense_acc.append(acc)
                dense_perf.append(perf)
                dense_commit.append(commit_id)
            elif model_type == "MoE":
                moe_date.append(date)
                moe_acc.append(acc)
                moe_perf.append(perf)
                moe_commit.append(commit_id)
    except Exception:
        traceback.print_stack()

    return dense_date, moe_date, dense_commit, moe_commit, dense_acc, moe_acc, dense_perf, moe_perf
