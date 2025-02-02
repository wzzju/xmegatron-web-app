#!/usr/bin/env bash

unset http_proxy https_proxy

ES_USR=${1:-"usr"}
ES_PWD=${2:-"123"}
ES_ADDR=${3:-"172.219.129.21:8901"}
INDEX_NAME=${4-"quality_monitor"}

# 1. 创建名为quality_monitor索引
curl -u "$ES_USR:$ES_PWD" -X PUT "$ES_ADDR/$INDEX_NAME?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "created_at": {
        "type": "date",
        "format": "EEE MMM d HH:mm:ss yyyy Z||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
      },
      "commit_id": {"type": "keyword"},
      "commit_message": {"type": "text", "analyzer": "standard"},
      "model_type": {"type": "keyword", "fields": {"raw": {"type": "keyword"}}},
      "acc": {"type": "float"},
      "perf": {"type": "float"}
    }
  },
  "settings": {"number_of_shards": 1, "number_of_replicas": 0}
}
'

# 2. 向quality_monitor索引中插入一条文档（自动生成ID）
curl -u "$ES_USR:$ES_PWD" -X POST "$ES_ADDR/$INDEX_NAME/_doc?pretty" -H 'Content-Type: application/json' -d'
{
  "created_at" : "Wed Jan 22 00:03:35 2025 +0800",
  "commit_id" : "b78c709d6e2c",
  "commit_message" : "优化调度性能",
  "model_type" : "Dense",
  "acc" : 2.15,
  "perf" : 311.66
}
'

# 3. 查询quality_monitor索引中的文档
curl -u "$ES_USR:$ES_PWD" -X GET "$ES_ADDR/$INDEX_NAME/_search?pretty"
curl -u "$ES_USR:$ES_PWD" -X GET "$ES_ADDR/$INDEX_NAME/_search?pretty&size=300"
curl -u "$ES_USR:$ES_PWD" -X GET "$ES_ADDR/$INDEX_NAME/_search?pretty&from=10&size=20"
curl -u "$ES_USR:$ES_PWD" -X GET "$ES_ADDR/$INDEX_NAME/_search?pretty" -H "Content-Type: application/json" -d'
{
  "query": {
    "match_all": {}
  },
  "size": 300
}
'
curl -u "$ES_USR:$ES_PWD" -X GET "$ES_ADDR/$INDEX_NAME/_search?pretty" -H "Content-Type: application/json" -d'
{
	"query": {
    "range": {
      "created_at": {
        "gte": "2025-01-26",
        "lte": "2025-02-01"
      }
    }
  },
  "sort": [{"created_at": {"order": "desc"}}],
  "size": 100
}
'

# 4. 删除 ID 为 Ze3uxZQBUhMXi7DL5-md 的文档
curl -u "$ES_USR:$ES_PWD" -X DELETE "$ES_ADDR/$INDEX_NAME/_doc/Ze3uxZQBUhMXi7DL5-md?pretty"

# 5. 删除quality_monitor整个索引内容
curl -u "$ES_USR:$ES_PWD" -X DELETE "$ES_ADDR/$INDEX_NAME"
