# Pro DNS Benchmarking Utility

A powerful and visually appealing CLI tool to benchmark DNS resolver performance and reliability.

## Features

- **Multi-Resolver Support:** Test multiple DNS servers simultaneously (e.g., Cloudflare, Google, local).
- **Comprehensive Metrics:** Measures average latency, minimum/maximum latency, jitter (standard deviation), and reliability percentage.
- **Rich UI:** Beautifully formatted tables and progress bars using the `rich` library.
- **Customizable:** Configure test domains, number of iterations, and thread count.
- **JSON Output:** Export results for further analysis or integration.
- **Parallel Execution:** Uses threading to perform benchmarks efficiently.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "Python DNS tester"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the utility with default resolvers (Cloudflare, Google):

```bash
python main.py
```

### Advanced Usage

Specify custom resolvers:
```bash
python main.py 1.1.1.1 8.8.8.8 9.9.9.9
```

Customize domains and iterations:
```bash
python main.py 1.1.1.1 -d google.com example.com -i 10
```

Output results as JSON:
```bash
python main.py --json
```

### Arguments

| Argument | Shorthand | Description | Default |
|----------|-----------|-------------|---------|
| `resolvers` | N/A | List of DNS IPs to test | `1.1.1.1`, `8.8.8.8` |
| `--domains` | `-d` | Domains to test against | Top 10 industry standard domains |
| `--iterations`| `-i` | Queries per domain per resolver | `5` |
| `--workers` | `-w` | Max parallel threads | `10` |
| `--json` | `-j` | Output results as JSON | `False` |

## Dependencies

- `dnspython`: For performing DNS lookups.
- `rich`: For the terminal user interface.

## License

MIT

## Sample Leaderboard

Here is an example of what the leaderboard looks like when testing popular public DNS resolvers:

| Resolver IP | Avg Latency | Min | Max | Jitter | Reliability |
|-------------|-------------|-----|-----|--------|-------------|
| 1.1.1.1 (Cloudflare) | 12.45 ms | 10.20 ms | 15.30 ms | 1.20 ms | 100.0% |
| 8.8.8.8 (Google) | 24.12 ms | 22.10 ms | 28.50 ms | 2.15 ms | 100.0% |
| 9.9.9.9 (Quad9) | 35.67 ms | 30.00 ms | 45.20 ms | 5.40 ms | 100.0% |
| 100.100.100.100 | 145.20 ms | 120.00 ms | 180.00 ms | 25.10 ms | 98.0% |

*Note: Results vary based on your geographic location and network conditions.*
