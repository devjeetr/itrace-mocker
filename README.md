## Setup
**Python 3 only**

```
    pip install -r requirements.txt
```


## Usage

Run mocker @5000hz with random data
```
python mocker.py --freq 5000
```

Save mock data used to `mock-data.json`
```
python mocker.py --freq 5000 --save


# generate mock data where x goes from 400-900
# and y goes from 300 - 700
python mocker.py --x 400:900 --y 300:700
```

**You might need to adjust the x & y ranges so that they correspond to valid line/col numbers, otherwise plugins might not even try to perform a lookup and give inaccurate assessments of performance**

Use custom mock-data:
```
python mocker.py --data ./data.json

```

Set session duration:

```
# run experiment for 10 seconds
python mocker.py --duration 10

# run experiment for 5 minutes
python mocker.py --duration 5m
```

For help
```
python mocker.py -h
```


## Bonus

You can use `listener.py` to mock an iTrace plugin. Use this to check what is the real world throughput of the `mocker.py` as a sanity check.

```

# start mocker
python mocker.py

# start listener, in another terminal
python listener.py

```

