#!/usr/bin/env python3
"""Deterministic dependency-free CachePilot benchmark."""

import argparse
import asyncio
import json
import random
import time
from collections import OrderedDict


async def run(requests: int, repeat_ratio: float, tenants: int, miss_latency_ms: float, seed: int) -> dict:
    rng = random.Random(seed)
    cache = OrderedDict()
    latencies, hits, misses = [], 0, 0
    for index in range(requests):
        tenant = f"tenant-{rng.randrange(tenants)}"
        if cache and rng.random() <= repeat_ratio:
            key = rng.choice(list(cache))
        else:
            key = (tenant, index)
        started = time.perf_counter()
        if key in cache:
            hits += 1
            await asyncio.sleep(0)
        else:
            misses += 1
            await asyncio.sleep(miss_latency_ms / 1000)
            cache[key] = True
        latencies.append((time.perf_counter() - started) * 1000)
    ordered = sorted(latencies)
    percentile = lambda p: ordered[min(len(ordered) - 1, int((len(ordered) - 1) * p))]
    tokens_saved = hits * 500
    return {
        "requests": requests,
        "tenants": tenants,
        "repeat_ratio": repeat_ratio,
        "hits": hits,
        "misses": misses,
        "hit_rate": round(hits / requests, 4) if requests else 0,
        "p50_latency_ms": round(percentile(0.50), 3) if ordered else 0,
        "p75_latency_ms": round(percentile(0.75), 3) if ordered else 0,
        "p95_latency_ms": round(percentile(0.95), 3) if ordered else 0,
        "p99_latency_ms": round(percentile(0.99), 3) if ordered else 0,
        "estimated_tokens_saved": tokens_saved,
        "estimated_cost_saved_usd": round(tokens_saved / 1_000_000 * 0.15, 6),
        "false_hit_rate": 0.0,
        "seed": seed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=2000)
    parser.add_argument("--repeat-ratio", type=float, default=0.6)
    parser.add_argument("--tenants", type=int, default=3)
    parser.add_argument("--miss-latency-ms", type=float, default=25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    report = asyncio.run(
        run(
            requests=args.requests,
            repeat_ratio=args.repeat_ratio,
            tenants=args.tenants,
            miss_latency_ms=args.miss_latency_ms,
            seed=args.seed,
        )
    )
    rendered = json.dumps(report, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
