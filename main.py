#!/usr/bin/env python3
import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import dns.resolver
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.live import Live

# Industry Standard Defaults
DEFAULT_DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "instagram.com",
    "chatgpt.com", "reddit.com", "wikipedia.org", "x.com",
    "whatsapp.com", "amazon.com"
]

console = Console()

class DNSBenchmarker:
    def __init__(self, resolvers: List[str], domains: List[str], iterations: int = 5, workers: int = 10):
        self.resolvers = resolvers
        self.domains = domains
        self.iterations = iterations
        self.workers = workers
        self.results = {}

    def _test_single_resolver(self, ip: str, progress, task_id) -> Dict[str, Any]:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [ip]
        resolver.timeout = 2.0
        resolver.lifetime = 2.0
        
        latencies = []
        success_count = 0
        total_queries = len(self.domains) * self.iterations

        for domain in self.domains:
            # Warm-up (standard practice to avoid caching bias)
            try:
                resolver.resolve(domain, "A")
            except Exception:
                pass

            for _ in range(self.iterations):
                try:
                    start = time.perf_counter()
                    resolver.resolve(domain, "A")
                    end = time.perf_counter()
                    latencies.append((end - start) * 1000)
                    success_count += 1
                except (dns.resolver.Timeout, dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                    pass
                except Exception as e:
                    # Log internal error but keep moving
                    pass
                progress.advance(task_id, 1)

        if not latencies:
            return {"error": "No successful resolutions"}

        return {
            "avg": statistics.mean(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "std_dev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "reliability": (success_count / total_queries) * 100
        }

    def run(self):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                futures = {}
                for ip in self.resolvers:
                    task_id = progress.add_task(f"Benchmarking {ip}...", total=len(self.domains) * self.iterations)
                    futures[executor.submit(self._test_single_resolver, ip, progress, task_id)] = ip

                for future in as_completed(futures):
                    ip = futures[future]
                    self.results[ip] = future.result()

    def display(self, sort_by: str = "avg"):
        table = Table(title="DNS Benchmark Leaderboard", title_style="bold magenta", border_style="bright_blue")
        table.add_column("Resolver IP", style="cyan", no_wrap=True)
        table.add_column("Avg Latency", justify="right")
        table.add_column("Min", justify="right")
        table.add_column("Max", justify="right")
        table.add_column("Jitter (StdDev)", justify="right")
        table.add_column("Reliability", justify="right")

        # Sort results based on user preference
        sorted_ips = sorted(
            [ip for ip in self.results if "error" not in self.results[ip]],
            key=lambda x: self.results[x].get(sort_by, 0)
        )

        for ip in sorted_ips:
            s = self.results[ip]
            # Color coding for performance
            color = "green" if s['avg'] < 30 else "yellow" if s['avg'] < 70 else "red"
            
            table.add_row(
                ip,
                f"[{color}]{s['avg']:>6.2f} ms[/{color}]",
                f"{s['min']:>6.2f} ms",
                f"{s['max']:>6.2f} ms",
                f"{s['std_dev']:>6.2f} ms",
                f"{'[bold green]' if s['reliability'] == 100 else '[bold red]'}{s['reliability']:>6.1f}%[/]"
            )
        
        # Add errored resolvers at the bottom
        for ip, s in self.results.items():
            if "error" in s:
                table.add_row(ip, f"[red]{s['error']}[/]", "-", "-", "-", "0.0%")

        console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Pro DNS Benchmarking Utility")
    parser.add_argument("resolvers", nargs="*", help="List of DNS IPs to test", default=["1.1.1.1", "8.8.8.8"])
    parser.add_argument("-d", "--domains", nargs="+", help="Domains to test against", default=DEFAULT_DOMAINS)
    parser.add_argument("-i", "--iterations", type=int, default=5, help="Queries per domain")
    parser.add_argument("-j", "--json", action="store_true", help="Output results as JSON")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Max parallel threads")
    
    args = parser.parse_args()

    bench = DNSBenchmarker(args.resolvers, args.domains, args.iterations, args.workers)
    bench.run()

    if args.json:
        print(json.dumps(bench.results, indent=4))
    else:
        bench.display()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Aborted by user.[/]")
        sys.exit(1)