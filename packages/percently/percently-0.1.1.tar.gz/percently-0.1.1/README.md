# percently

## Motivation

A fast percentile calculator written in rust, to use to calculate the buckets etc. after performing a loadtest, etc.

## Installation

```
uv add percently
```

or

```
pip install percet
```

## 🧮 Usage
```
import percently

# Example data
data = [10.5, 22.0, 18.7, 19.2, 30.1, 25.3]

# Calculate the 95th percentlyile (f64)
p95 = percently.percentlyile(data, 95)
print(f"95th percentlyile: {p95:.2f}")

Example output
95th percentlyile: 29.12
```
