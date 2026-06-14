"""Create bundled sample Q&A dataset for ingestion."""

import json
from pathlib import Path

SAMPLE = [
    {
        "title": "How to read a CSV file using pandas",
        "question": "I have a CSV file on disk. What is the standard way to load it into a pandas DataFrame?",
        "answer": "Use pandas.read_csv. Example: import pandas as pd; df = pd.read_csv('data.csv'). For large files use chunksize or dtype options. You can also pass usecols to load selected columns only.",
    },
    {
        "title": "Difference between list and tuple in Python",
        "question": "What is the difference between a Python list and a tuple?",
        "answer": "Lists are mutable sequences created with square brackets []. Tuples are immutable sequences created with parentheses (). Tuples can be used as dict keys and are often faster for fixed collections.",
    },
    {
        "title": "Handling missing values in pandas",
        "question": "How do I handle NaN or missing values in a pandas DataFrame?",
        "answer": "Detect missing values with df.isna() or df.isnull(). Drop rows with df.dropna() or fill with df.fillna(value) or df.fillna(method='ffill'). Use df.interpolate() for numeric gaps.",
    },
    {
        "title": "Python list comprehension example",
        "question": "Explain list comprehensions with an example.",
        "answer": "A list comprehension builds a list in one line: squares = [x*x for x in range(10)]. You can add filters: evens = [x for x in range(20) if x % 2 == 0].",
    },
    {
        "title": "Install packages with pip",
        "question": "How do I install Python packages using pip?",
        "answer": "Run pip install package_name in your terminal. Example: pip install pandas. Use pip install -r requirements.txt to install from a file. Prefer python -m pip install inside virtual environments.",
    },
    {
        "title": "What is a Python decorator",
        "question": "What is a decorator in Python and how do I write one?",
        "answer": "A decorator wraps a function to extend behavior without changing its source. Example: def logger(fn): def wrapper(*args, **kwargs): print('calling', fn.__name__); return fn(*args, **kwargs); return wrapper. Apply with @logger above a function definition.",
    },
    {
        "title": "Merge two DataFrames in pandas",
        "question": "How do I merge two pandas DataFrames?",
        "answer": "Use pd.merge(left, right, on='key', how='inner'). Other joins: left, right, outer. For index-based joins use df.join(). Concatenate vertically with pd.concat([df1, df2], ignore_index=True).",
    },
    {
        "title": "What is the GIL in Python",
        "question": "What is the Global Interpreter Lock (GIL) in Python?",
        "answer": "The GIL is a mutex in CPython that allows only one thread to execute Python bytecode at a time in a single process. It simplifies memory management but limits CPU-bound multithreading. Use multiprocessing for CPU parallelism.",
    },
    {
        "title": "Catch exceptions in Python",
        "question": "How do I catch exceptions in Python?",
        "answer": "Use try/except: try: risky() except ValueError as e: handle(e) else: success_path() finally: cleanup(). Catch specific exceptions instead of bare except.",
    },
    {
        "title": "Convert string to integer safely",
        "question": "How do I convert a string to an integer safely in Python?",
        "answer": "Use int(text) inside try/except ValueError. For user input: value = int(input('Enter number: ')). Validate with text.isdigit() for positive integers only.",
    },
    {
        "title": "Read JSON file in Python",
        "question": "How do I read a JSON file in Python?",
        "answer": "import json; with open('file.json') as f: data = json.load(f). Write with json.dump(data, f, indent=2). For strings use json.loads and json.dumps.",
    },
    {
        "title": "Virtual environment in Python",
        "question": "How do I create and use a virtual environment?",
        "answer": "Create with python -m venv .venv. Activate: source .venv/bin/activate on Linux/Mac or .venv\\Scripts\\activate on Windows. Install packages inside the venv to isolate dependencies.",
    },
    {
        "title": "Sort dictionary by value",
        "question": "How do I sort a dictionary by value in Python?",
        "answer": "sorted_items = sorted(d.items(), key=lambda kv: kv[1]). In Python 3.7+ dicts preserve insertion order. Use collections.Counter for frequency sorting.",
    },
    {
        "title": "Write to CSV with pandas",
        "question": "How do I export a DataFrame to CSV?",
        "answer": "df.to_csv('output.csv', index=False). Use sep='\\t' for TSV. Control missing values with na_rep. For Excel use df.to_excel('out.xlsx', index=False) with openpyxl installed.",
    },
    {
        "title": "Python f-strings formatting",
        "question": "How do f-strings work in Python?",
        "answer": "f-strings embed expressions: name='Ada'; msg=f'Hello {name}'. Supports formatting: f'{pi:.2f}'. Available in Python 3.6+ and preferred over % or .format for readability.",
    },
    {
        "title": "Check if key exists in dictionary",
        "question": "How do I check whether a key exists in a dict?",
        "answer": "Use 'key' in my_dict. Retrieve safely with my_dict.get('key', default). Avoid my_dict['key'] unless you want KeyError on missing keys.",
    },
    {
        "title": "Iterate over DataFrame rows",
        "question": "How do I loop over rows in a pandas DataFrame?",
        "answer": "Prefer vectorized operations. If needed use df.itertuples() for speed or df.iterrows() for Series pairs. Avoid repeated row-wise loops on large frames.",
    },
    {
        "title": "Remove duplicates pandas",
        "question": "How do I remove duplicate rows in pandas?",
        "answer": "df.drop_duplicates() removes exact duplicate rows. Pass subset=['col'] to dedupe by columns and keep='first' or keep='last'.",
    },
    {
        "title": "GroupBy aggregate pandas",
        "question": "How does groupby work in pandas?",
        "answer": "df.groupby('category')['sales'].sum(). Chain multiple aggregations: df.groupby('category').agg(total=('sales','sum'), avg=('sales','mean')). Reset index with .reset_index().",
    },
    {
        "title": "Python argparse tutorial",
        "question": "How do I parse command line arguments in Python?",
        "answer": "Use argparse: parser = argparse.ArgumentParser(); parser.add_argument('--limit', type=int, default=10); args = parser.parse_args(). Access args.limit in your script.",
    },
    {
        "title": "Async await basics FastAPI",
        "question": "Why use async def in FastAPI endpoints?",
        "answer": "async endpoints allow non-blocking I/O while waiting on network or disk. FastAPI runs sync endpoints in a threadpool. Use async when calling async libraries like httpx.AsyncClient.",
    },
    {
        "title": "Type hints in Python",
        "question": "What are Python type hints?",
        "answer": "Type hints annotate expected types: def greet(name: str) -> str: return f'Hi {name}'. They are optional at runtime but help static checkers like mypy and improve IDE support.",
    },
    {
        "title": "Python enumerate function",
        "question": "What does enumerate do in Python?",
        "answer": "enumerate(iterable) yields (index, item) pairs: for i, value in enumerate(['a','b']): print(i, value). Start index at 1 with enumerate(items, start=1).",
    },
    {
        "title": "Split string Python",
        "question": "How do I split strings in Python?",
        "answer": "text.split(',') splits on comma. Use text.split() for whitespace. For regex splitting import re; re.split(r'\\s+', text). Join with ','.join(parts).",
    },
    {
        "title": "Datetime parsing pandas",
        "question": "How do I parse dates in pandas?",
        "answer": "pd.to_datetime(df['date_col']). Pass format='%Y-%m-%d' for explicit patterns. Use df['date'].dt.year to extract components after conversion.",
    },
    {
        "title": "Requests GET example",
        "question": "How do I make HTTP GET requests in Python?",
        "answer": "import requests; r = requests.get('https://api.example.com/data', timeout=30); r.raise_for_status(); data = r.json(). Set headers and params as needed.",
    },
    {
        "title": "Context manager with statement",
        "question": "What is a context manager in Python?",
        "answer": "Context managers guarantee setup/teardown with the with statement: with open('file.txt') as f: content = f.read(). Implement __enter__ and __exit__ or use contextlib.contextmanager.",
    },
    {
        "title": "Set vs list Python",
        "question": "When should I use a set instead of a list?",
        "answer": "Sets store unique unordered elements and support fast membership tests. Use set(list_items) to deduplicate. Operations include union, intersection, and difference.",
    },
    {
        "title": "Map filter lambda Python",
        "question": "Explain map, filter, and lambda in Python.",
        "answer": "lambda creates small anonymous functions: lambda x: x*2. map(fn, iterable) applies fn to each item. filter(fn, iterable) keeps items where fn returns True. List comprehensions often replace these.",
    },
    {
        "title": "Read Excel pandas",
        "question": "How do I read Excel files with pandas?",
        "answer": "pd.read_excel('file.xlsx', sheet_name='Sheet1'). Requires openpyxl or xlrd depending on format. Read all sheets with sheet_name=None returning a dict of DataFrames.",
    },
]

# Expand with variations for richer retrieval corpus
EXTRA_TOPICS = [
    ("numpy array creation", "Create arrays with import numpy as np; arr = np.array([1,2,3]). Use np.zeros, np.ones, np.arange, and np.linspace for common patterns."),
    ("matplotlib basic plot", "import matplotlib.pyplot as plt; plt.plot(x, y); plt.xlabel('x'); plt.ylabel('y'); plt.title('Title'); plt.show()."),
    ("scikit-learn train test split", "from sklearn.model_selection import train_test_split; X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)."),
    ("python pathlib usage", "from pathlib import Path; p = Path('data/file.txt'); p.exists(); p.read_text(); p.parent.mkdir(parents=True, exist_ok=True)."),
    ("python logging basicConfig", "import logging; logging.basicConfig(level=logging.INFO); logger = logging.getLogger(__name__); logger.info('message')."),
    ("python dataclass example", "from dataclasses import dataclass; @dataclass class User: name: str; age: int; u = User('Ann', 30)."),
    ("python zip function", "pairs = list(zip([1,2], ['a','b'])). Unzip with a, b = zip(*pairs). Useful for parallel iteration."),
    ("python any all functions", "any(iterable) returns True if any element is truthy. all(iterable) returns True if all elements are truthy."),
    ("pandas apply function", "df['col2'] = df['col1'].apply(lambda x: x * 2). For row-wise logic use axis=1 carefully or prefer vectorization."),
    ("pandas query method", "df.query('age > 30 and city == \"NYC\"') filters rows using a string expression."),
    ("python property decorator", "@property def volume(self): return self.width * self.height. Use for computed attributes with getter semantics."),
    ("python super init", "class Child(Parent): def __init__(self, x): super().__init__(); self.x = x. Calls parent initializer in inheritance."),
    ("python copy deepcopy", "import copy; shallow = copy.copy(obj); deep = copy.deepcopy(obj). Deep copy duplicates nested structures."),
    ("python hashable types", "Dict keys must be hashable: str, int, tuple of hashables. Lists are not hashable and cannot be dict keys."),
    ("python generator yield", "def gen(): yield 1; yield 2. Generators produce lazy sequences and save memory for large streams."),
    ("python itertools combinations", "from itertools import combinations; list(combinations([1,2,3], 2)) gives pairs without repetition."),
    ("python collections Counter", "from collections import Counter; Counter(['a','b','a']).most_common(1) counts frequencies."),
    ("python collections defaultdict", "from collections import defaultdict; d = defaultdict(list); d['key'].append(1) avoids KeyError."),
    ("python unittest example", "import unittest; class TestMath(unittest.TestCase): def test_add(self): self.assertEqual(1+1, 2). Run with unittest.main()."),
    ("python pytest parametrize", "import pytest; @pytest.mark.parametrize('x,y,expected', [(1,2,3)]) def test_add(x,y,expected): assert x+y == expected."),
    ("python regex re search", "import re; m = re.search(r'\\d+', 'abc123'); m.group() if m else None extracts first digit sequence."),
    ("python os path join", "import os; path = os.path.join('data', 'file.csv'). Prefer pathlib Path for modern code."),
    ("python subprocess run", "import subprocess; subprocess.run(['python', '--version'], check=True, capture_output=True, text=True)."),
    ("python json serializable datetime", "Convert datetime with default=str in json.dumps or custom JSONEncoder because datetime is not JSON serializable by default."),
    ("python pandas melt", "pd.melt(df, id_vars=['id'], value_vars=['A','B']) converts wide to long format."),
    ("python pandas pivot", "df.pivot(index='date', columns='category', values='sales') reshapes data."),
    ("python pandas concat axis", "pd.concat([df1, df2], axis=0) stacks vertically; axis=1 joins horizontally."),
    ("python seaborn scatterplot", "import seaborn as sns; sns.scatterplot(data=df, x='x', y='y', hue='category')."),
    ("python train validation leakage", "Always split before preprocessing fit steps. Use Pipeline in sklearn to avoid data leakage."),
    ("python pickle security", "Never unpickle untrusted data. pickle can execute arbitrary code during load."),
]

records = []
for i, item in enumerate(SAMPLE, start=1):
    records.append({"Id": i, "Title": item["title"], "Body_question": item["question"], "Body_answer": item["answer"], "Score_answer": 100 - i})

start = len(records) + 1
for j, (title, answer) in enumerate(EXTRA_TOPICS, start=start):
    records.append(
        {
            "Id": j,
            "Title": title.replace("_", " ").title(),
            "Body_question": f"Can you explain {title} in Python?",
            "Body_answer": answer,
            "Score_answer": max(10, 120 - j),
        }
    )

out = Path(__file__).resolve().parent.parent / "data" / "sample" / "sample_qa.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(records, indent=2), encoding="utf-8")
print(f"Wrote {len(records)} records to {out}")
