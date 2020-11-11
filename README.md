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
```

Use custom mock-data:
```
python mocker.py --data ./data.json
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

