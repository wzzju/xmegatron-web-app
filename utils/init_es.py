import time
from datetime import datetime, timedelta

import pytz
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tabulate import tabulate

DATE_FMT = "%a %b %-d %H:%M:%S %Y %z"
TIME_ZONE = "Asia/Shanghai"
INDEX_NAME = "quality_monitor"
ES_ADDR = ["http://172.219.129.21:8901"]
ES_USR = "usr"
ES_PWD = "123"


def connect_es(addr=ES_ADDR, usr=ES_USR, pwd=ES_PWD):
    es = Elasticsearch(addr, basic_auth=(usr, pwd))

    if es.ping():
        print("Successfully connected to Elasticsearch!")
    else:
        raise Exception("Could not connect to Elasticsearch.")
    return es


def create_index(es, index_name):
    mapping = {
        "mappings": {
            "properties": {
                "created_at": {
                    "type": "date",
                    # 支持四种日期格式：git显示时间戳、完整时间戳、纯日期、毫秒时间戳
                    "format": "EEE MMM d HH:mm:ss yyyy Z||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis",
                },
                # keyword：不分词的文本，用于精确匹配，支持排序和聚合
                "trigger_repo": {"type": "keyword"},
                "xmlir_commit": {"type": "keyword"},
                "llm_commit": {"type": "keyword"},
                "mextension_commit": {"type": "keyword"},
                "mcore_commit": {"type": "keyword"},
                # model_type 使用 text 类型，表示会被分词的文本，用于全文搜索，适合搜索部分匹配关键词的情况，默认不支持排序和聚合
                # model_type.raw 使用 keyword 类型，表示不分词的文本，用于聚合和排序
                "model_type": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "acc": {"type": "float"},
                "perf": {"type": "float"},
            }
        },
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    }
    if not es.indices.exists(index=index_name):
        try:
            es.indices.create(index=index_name, body=mapping)
            print(f"Index '{index_name}' created.")
        except Exception as e:
            print(f"Index created error: {e}")
    else:
        print(f"Index '{index_name}' already exists.")


def insert_data(es, index_name):
    import random
    import string

    def generate_commit_id():
        alpha_1 = ''.join(random.choices(string.ascii_lowercase, k=2))
        num_1 = ''.join(random.choices(string.digits, k=2))
        alpha_2 = ''.join(random.choices(string.ascii_lowercase, k=2))
        num_2 = ''.join(random.choices(string.digits, k=1))
        return f"{alpha_1}{num_1}{alpha_2}{num_2}"

    one_doc = {
        "created_at": "Sat Feb 1 12:26:23 2025 +0800",
        "trigger_repo": "XMLIR",
        "xmlir_commit": f"master@{generate_commit_id()}",
        "llm_commit": f"master@{generate_commit_id()}",
        "mextension_commit": f"master@{generate_commit_id()}",
        "mcore_commit": f"core_r0.10.0@{generate_commit_id()}",
        "model_type": "Dense",
        "acc": 2.15,
        "perf": 305.42,
    }
    es.index(index=index_name, body=one_doc)
    print("Single document inserted.")

    def generate_sample_data(num=100):
        data = []
        commit_ids = [generate_commit_id() for i in range(4 * num)]
        repos = [
            "XMLIR",
            "KLX-Megatron-Extension",
            "KLX-LLM",
        ]

        for i in range(num):
            model_type = random.choice(["Dense", "MoE"])
            branches = random.choice(["main", "dev", "dev_0.10.0"])
            doc = {
                "created_at": (
                    datetime.now(pytz.timezone(TIME_ZONE))
                    - timedelta(
                        days=random.randint(1, 100),
                        hours=random.randint(0, num // (i + 1)) + 2 * i,
                    )
                ).strftime(DATE_FMT),
                "trigger_repo": random.choice(repos),
                "xmlir_commit": f"master@{commit_ids[i * 4]}",
                "llm_commit": f"master@{commit_ids[i * 4 + 1]}",
                "mextension_commit": f"{branches}@{commit_ids[i * 4 + 2]}",
                "mcore_commit": f"core_r0.10.0@{commit_ids[i * 4 + 3]}",
                "model_type": model_type,
                "acc": (
                    round(random.uniform(2.2, 2.5), 2)
                    if model_type == "Dense"
                    else round(random.uniform(7.2, 7.5), 2)
                ),
                "perf": (
                    round(random.uniform(300, 310), 2)
                    if model_type == "Dense"
                    else round(random.uniform(200, 210), 2)
                ),
            }

            action = {"_index": index_name, "_source": doc}
            data.append(action)

        return data

    docs = generate_sample_data(300)
    bulk(es, docs)
    print("Bulk documents inserted.")


def search_data(es, index_name):
    query_all = {"query": {"match_all": {}}, "size": 20}
    result = es.search(index=index_name, body=query_all)
    print(f"Get {result['hits']['total']['value']} documents:")
    for hit in result["hits"]["hits"]:
        print(f"ID: {hit['_id']}, Data: {hit['_source']}")
    print("-" * 120)

    now = datetime.now(pytz.timezone(TIME_ZONE))
    month_ago = now - timedelta(days=30)
    query_conditions = {
        "query": {
            "range": {
                "created_at": {
                    "gte": month_ago.strftime(DATE_FMT),
                    "lte": now.strftime(DATE_FMT),
                }
            }
        },
        "sort": [{"created_at": {"order": "desc"}}],  # 按时间降序排序
        "size": 100,  # 最多返回100个查询结果
    }
    try:
        response = es.search(index=index_name, body=query_conditions)
        print(f"Find {response['hits']['total']['value']} records:")
        for hit in response['hits']['hits']:
            doc = hit['_source']
            print(f"Model Type: {doc['model_type']}")
            print(f"Acc: {doc['acc']:.2f}")
            print(f"Perf: {doc['perf']:.2f}")
            print(
                f"Trigger Repo: {doc['trigger_repo']}\n"
                + f"MLIR Commit: {doc['xmlir_commit']}\n"
                + f"LLM Commit: {doc['llm_commit']}\n"
                + f"MExtension Commit: {doc['mextension_commit']}\n"
                + f"MCore Commit: {doc['mcore_commit']}"
            )
            print(f"Date: {doc['created_at']}")
            print("*" * 120)
    except Exception as e:
        print(f"Query Error: {e}")
    query_conditions = {
        "query": {
            # 使用 bool 查询组合多个条件
            "bool": {
                # must 表示所有条件都必须满足（相当于 AND）
                "must": [
                    # 条件1：查询最近一个月的数据
                    {
                        "range": {
                            "created_at": {
                                "gte": month_ago.strftime(DATE_FMT),
                                "lte": now.strftime(DATE_FMT),
                            }
                        }
                    },
                    # 条件2：模型类型必须是 Dense 或 MoE
                    {"terms": {"model_type.raw": ["Dense", "MoE"]}},  # 按模型类型过滤
                ]
            }
        },
        "sort": [
            {"model_type.raw": {"order": "asc"}},  # 先按模型类型升序
            {"created_at": {"order": "desc"}},  # 再按时间降序
        ],
        "size": 100,  # 返回结果数量限制
        "aggs": {  # 添加聚合分析
            "model_types": {
                # 按模型类型分组（最多10种类型）
                "terms": {"field": "model_type.raw", "size": 10},
                # 对每种模型类型计算：最高准确率、最低准确率、最高性能和最低性能
                "aggs": {
                    "max_acc": {"max": {"field": "acc"}},
                    "min_acc": {"min": {"field": "acc"}},
                    "max_perf": {"max": {"field": "perf"}},
                    "min_perf": {"min": {"field": "perf"}},
                },
            }
        },
    }
    try:
        response = es.search(index=index_name, body=query_conditions)
        # 打印聚合结果
        print("\n=== 模型性能统计 ===")
        headers = ["模型类型", "数据量", "最高准确率", "最低准确率", "最高性能", "最低性能"]
        stats_data = []

        for bucket in response['aggregations']['model_types']['buckets']:
            stats_data.append(
                [
                    bucket['key'],
                    bucket['doc_count'],
                    f"{bucket['max_acc']['value']:.2f}",
                    f"{bucket['min_acc']['value']:.2f}",
                    f"{bucket['max_perf']['value']:.2f}",
                    f"{bucket['min_perf']['value']:.2f}",
                ]
            )

        print(tabulate(stats_data, headers=headers, tablefmt="grid"))

        # 打印详细数据
        print("\n=== Detail Data ===")
        headers = [
            "Date",
            "Trigger Repo",
            "XMLIR Commit",
            "LLM Commit",
            "MExtension Commit",
            "MCore Commit",
            "Mode Type",
            "Acc",
            "Perf",
        ]
        details_data = []

        for hit in response['hits']['hits']:
            doc = hit['_source']
            details_data.append(
                [
                    doc['created_at'],
                    doc['trigger_repo'],
                    doc['xmlir_commit'],
                    doc['llm_commit'],
                    doc['mextension_commit'],
                    doc['mcore_commit'],
                    doc['model_type'],
                    f"{doc['acc']:.2f}",
                    f"{doc['perf']:.2f}",
                ]
            )

        print(tabulate(details_data, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"Query Error: {e}")


def cleanup(es, index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"\nIndex '{index_name}' deleted.")


def main():
    index_name = INDEX_NAME
    es = connect_es()

    try:
        create_index(es, index_name)
        time.sleep(1)

        insert_data(es, index_name)
        time.sleep(1)

        search_data(es, index_name)
    finally:
        # cleanup(es, index_name)
        es.close()


if __name__ == "__main__":
    main()
