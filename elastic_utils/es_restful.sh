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
      "commit_date": {
        "type": "date",
        "format": "EEE MMM d HH:mm:ss yyyy Z||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
      },
      "trigger_repo": {"type": "keyword"},
      "xmlir_commit": {"type": "keyword"},
      "llm_commit": {"type": "keyword"},
      "mextension_commit": {"type": "keyword"},
      "mcore_commit": {"type": "keyword"},
      "model_type": {"type": "text", "analyzer": "standard", "fields": {"raw": {"type": "keyword"}}},
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
  "commit_date" : "Wed Jan 22 00:03:35 2025 +0800",
  "trigger_repo" : "XMLIR",
  "xmlir_commit" : "master@2bcd0b1",
  "llm_commit" : "master@cd7b6d4",
  "mextension_commit" : "master@I0375f8",
  "mcore_commit" : "core_r0.10.0@fa79b7c",
  "model_type" : "Dense",
  "acc" : 2.15,
  "perf" : 311.66
}
'
curl -u "$ES_USR:$ES_PWD" -X POST "$ES_ADDR/$INDEX_NAME/_doc?pretty" -H 'Content-Type: application/json' -d'
{
  "commit_date" : "Thu Jan 23 14:22:24 2025 +0800",
  "trigger_repo" : "KLX-Megatron-Extension",
  "xmlir_commit" : "master@2bcd0b1",
  "llm_commit" : "master@cd7b6d4",
  "mextension_commit" : "dev@c817156",
  "mcore_commit" : "core_r0.10.0@fa79b7c",
  "model_type" : "MoE",
  "acc" : 7.25,
  "perf" : 209.98
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
      "commit_date": {
        "gte": "2025-01-26",
        "lte": "2025-02-01"
      }
    }
  },
  "sort": [{"commit_date": {"order": "desc"}}],
  "size": 100
}
'

# 4. 删除 ID 为 Ze3uxZQBUhMXi7DL5-md 的文档
curl -u "$ES_USR:$ES_PWD" -X DELETE "$ES_ADDR/$INDEX_NAME/_doc/Ze3uxZQBUhMXi7DL5-md?pretty"

# 5. 删除quality_monitor整个索引内容
curl -u "$ES_USR:$ES_PWD" -X DELETE "$ES_ADDR/$INDEX_NAME"
