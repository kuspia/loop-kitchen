# loop-kitchen

Assignment: https://loopxyz.notion.site/Take-home-interview-Store-Monitoring-12664a3c7fdf472883a41457f0c9347d

## Installation 

To install the required packages, run the following command in the project directory:
```
    pip install -r requirements.txt
```

## Usage

To start the server, run the following command in the project directory:
```
    python run.py

```

The server will start running on http://localhost:5000


`/trigger_report` endpoint that will trigger report generation from the data provided (stored in DB)

![image](https://github.com/kuspia/loop-kitchen/assets/63403330/e1656a03-b4a5-4d3d-b7db-60f19335874e)

`/get_report` endpoint that will return the status of the report or the csv

![image](https://github.com/kuspia/loop-kitchen/assets/63403330/0b2c7dd2-2432-40a0-86df-dfa8105da25b)

After getting completed in few minutes CSV resposne is sent as shown:
