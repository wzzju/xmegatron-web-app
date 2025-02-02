import traceback
from datetime import datetime, timedelta

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


def search_data(start_date=None, end_date=None, index_name=INDEX_NAME, es=ES_CLIENT):
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

    query_conditions = {
        "query": {
            "range": {
                "created_at": {
                    "gte": start_date,
                    "lte": end_date,
                }
            }
        },
        "sort": [{"created_at": {"order": "desc"}}],  # 按时间降序排序
        "size": 1000,  # 最多返回1000个查询结果
    }

    dense_date, dense_acc, dense_perf, dense_commit = [], [], [], []
    moe_date, moe_acc, moe_perf, moe_commit = [], [], [], []
    try:
        response = es.search(index=index_name, body=query_conditions)
        for hit in response['hits']['hits']:
            doc = hit['_source']
            if doc['model_type'] == "Dense":
                dense_date.append(doc['created_at'])
                dense_acc.append(doc['acc'])
                dense_perf.append(doc['perf'])
                dense_commit.append(doc['commit_id'])
            elif doc['model_type'] == "MoE":
                moe_date.append(doc['created_at'])
                moe_acc.append(doc['acc'])
                moe_perf.append(doc['perf'])
                moe_commit.append(doc['commit_id'])
    except Exception:
        traceback.print_stack()

    return dense_date, moe_date, dense_commit, moe_commit, dense_acc, moe_acc, dense_perf, moe_perf
