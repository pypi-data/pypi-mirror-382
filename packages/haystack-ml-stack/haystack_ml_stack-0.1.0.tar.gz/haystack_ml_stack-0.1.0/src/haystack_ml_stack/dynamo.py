from typing import Any, Dict, List
import logging

import aiobotocore.session

logger = logging.getLogger(__name__)


async def async_batch_get(
    dynamo_client, table_name: str, keys: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Asynchronous batch_get_item with unprocessed keys handling."""
    all_items: List[Dict[str, Any]] = []
    to_fetch = {table_name: {"Keys": keys}}

    while to_fetch:
        resp = await dynamo_client.batch_get_item(RequestItems=to_fetch)
        all_items.extend(resp["Responses"].get(table_name, []))
        unprocessed = resp.get("UnprocessedKeys", {})
        to_fetch = unprocessed if unprocessed.get(table_name) else {}

    return all_items


def parse_dynamo_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a DynamoDB attribute map (low-level) to Python types."""
    out: Dict[str, Any] = {}
    for k, v in item.items():
        if "N" in v:
            out[k] = float(v["N"])
        elif "S" in v:
            out[k] = v["S"]
        elif "SS" in v:
            out[k] = v["SS"]
        elif "NS" in v:
            out[k] = [float(n) for n in v["NS"]]
        elif "BOOL" in v:
            out[k] = v["BOOL"]
        elif "NULL" in v:
            out[k] = None
        elif "L" in v:
            out[k] = [parse_dynamo_item({"value": i})["value"] for i in v["L"]]
        elif "M" in v:
            out[k] = parse_dynamo_item(v["M"])
    return out


async def set_stream_features(
    *,
    streams: List[Dict[str, Any]],
    stream_features: List[str],
    features_cache,
    features_table: str,
    stream_pk_prefix: str,
    cache_sep: str,
    aio_session: aiobotocore.session.Session | None = None,
) -> None:
    """Fetch missing features for streams from DynamoDB and fill them into streams."""
    if not streams or not stream_features:
        return

    cache_miss: Dict[str, Dict[str, Any]] = {}
    for f in stream_features:
        for s in streams:
            key = f"{s['streamUrl']}{cache_sep}{f}"
            cached = features_cache.get(key)
            if cached is not None:
                s[f] = cached["value"]
            else:
                cache_miss[key] = s

    if not cache_miss:
        return

    logger.info("Cache miss for %d items", len(cache_miss))

    # Prepare keys
    keys = []
    for k in cache_miss.keys():
        stream_url, sk = k.split(cache_sep, 1)
        pk = f"{stream_pk_prefix}{stream_url}"
        keys.append({"pk": {"S": pk}, "sk": {"S": sk}})

    session = aio_session or aiobotocore.session.get_session()
    async with session.create_client("dynamodb") as dynamodb:
        try:
            items = await async_batch_get(dynamodb, features_table, keys)
        except Exception as e:
            logger.error("DynamoDB batch_get failed: %s", e)
            return

    for item in items:
        stream_url = item["pk"]["S"].removeprefix(stream_pk_prefix)
        feature_name = item["sk"]["S"]
        cache_key = f"{stream_url}{cache_sep}{feature_name}"
        parsed = parse_dynamo_item(item)

        features_cache[cache_key] = {
            "value": parsed.get("value"),
            "cache_ttl_in_seconds": int(parsed.get("cache_ttl_in_seconds", -1)),
        }
        if cache_key in cache_miss:
            cache_miss[cache_key][feature_name] = parsed.get("value")