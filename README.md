## Flask Hotel Reviews App

A demo app using Flask and IBM Watson APIs to do sentiment analysis on hotel reviews.

### How to use

1. Download hotel reviews dataset from https://www.kaggle.com/datafiniti/hotel-reviews and place 7282_1.csv in data directoy
2. Install Elasticsearch from https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html
3. Register for IBM Watson API https://cloud.ibm.com/
4. Install Python library requirements:
- pandas
- numpy
- json
- json2html
- flask
- ibm-watson
- elasticsearch-py

5. Run
`python code/app.py`

6. Go to
`http://localhost:5000/`

7. Enter a hotel name and view an "Overview" of review tones or "Detailed" hotel information.
