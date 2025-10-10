# Luxin

[![PyPI version](https://badge.fury.io/py/luxin.svg)](https://badge.fury.io/py/luxin)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Interactive HTML tables with drill-down capabilities for exploring aggregated data in Jupyter notebooks and Streamlit apps.

## Demo

<!-- Uncomment when demo.gif is created
![Luxin Demo](https://raw.githubusercontent.com/eddiethedean/luxin/master/assets/demo.gif)
-->

**Click on aggregated rows to instantly see the underlying detail data in an interactive side panel.**

Try it yourself: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/eddiethedean/luxin/master?filepath=examples/01_getting_started.ipynb)

## Overview

Luxin allows you to create interactive tables that let you click on aggregated rows to see the underlying detail data. Like the magical substance from the Lightbringer series that can be shaped and manipulated, Luxin helps you shape and explore your data at different levels of granularity.

## Features

- 🔍 **Drill-down exploration**: Click on aggregated rows to see source data
- 📊 **Automatic tracking**: TrackedDataFrame automatically tracks source rows during aggregations
- 🎯 **Manual API**: Link aggregated and detail data manually for any workflow
- 📓 **Jupyter support**: Works seamlessly in Jupyter notebooks
- 🚀 **Streamlit support**: Build interactive Streamlit apps
- 🎨 **Modern UI**: Clean, responsive interface with side panel display

## Installation

```bash
pip install luxin
```

For Streamlit support:
```bash
pip install luxin[streamlit]
```

For Polars support:
```bash
pip install luxin[polars]
```

## Quick Start

### Automatic Tracking

```python
from luxin import TrackedDataFrame
import pandas as pd

# Create a TrackedDataFrame
df = TrackedDataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'sales': [100, 150, 200, 250, 300],
    'profit': [10, 15, 20, 25, 30]
})

# Aggregate data - tracking is automatic
agg = df.groupby(['category']).agg({'sales': 'sum', 'profit': 'sum'})

# Display with drill-down capability
agg.show_drill_table()
```

### Manual API

```python
from luxin import create_drill_table
import pandas as pd

# Your existing workflow
df = pd.DataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'sales': [100, 150, 200, 250, 300],
    'profit': [10, 15, 20, 25, 30]
})

agg_df = df.groupby(['category']).sum()

# Create interactive drill-down table
create_drill_table(agg_df, df, groupby_cols=['category'])
```

## How It Works

When you aggregate data, Luxin tracks which source rows contribute to each aggregated row. When you click on a row in the displayed table, a side panel slides in showing all the detail rows that were aggregated to create that summary.

## Use Cases

- Exploring sales data by region, then drilling into individual transactions
- Analyzing error logs by error type, then viewing specific error instances
- Reviewing survey responses by category, then reading individual responses
- Investigating performance metrics by service, then examining individual requests

## Examples

Check out the interactive example notebooks:

- [Getting Started](examples/01_getting_started.ipynb) - Basic usage and introduction
- [Sales Analysis](examples/02_sales_analysis.ipynb) - Real-world sales data exploration
- [Multi-Column Grouping](examples/03_multi_column_groupby.ipynb) - Advanced grouping techniques

You can also run these examples interactively in your browser:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/eddiethedean/luxin/master?filepath=examples)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

