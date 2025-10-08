# percently

## Motivation

A fast percentile calculator written in rust, to use to calculate the buckets etc. after performing a loadtest, etc.

## Installation

```
uv add percently
```

or

```
pip install percently
```

## 🧮 Usage
```
import percently

# Example data
data = [10.5, 22.0, 18.7, 19.2, 30.1, 25.3]

# Calculate the 95th percentile (f64)
p95 = percently.percentile(data, 95)
print(f"95th percentile: {p95:.2f}")

# Example output
95th percentile: 29.12
```
