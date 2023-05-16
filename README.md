# loop-kitchen

Assignment: https://loopxyz.notion.site/Take-home-interview-Store-Monitoring-12664a3c7fdf472883a41457f0c9347d
Demo: https://www.youtube.com/watch?v=NkYvkXqsXKI

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

![image](https://github.com/kuspia/loop-kitchen/assets/63403330/e09746a0-64f3-4761-b1e3-f596fd7be8ac)

`/get_report` endpoint that will return the status of the report or the csv

![image](https://github.com/kuspia/loop-kitchen/assets/63403330/3d7db446-beaa-4a15-a941-0f5c9df2108c)

After getting completed in few minutes CSV resposne is sent as shown:

![Uploading image.png…]()

