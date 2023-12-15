import boto3
import requests
import json
import time

# Set up the Kinesis client
# Set AWS credentials within the script
aws_access_key_id = 'key'
aws_secret_access_key = 'secret'
region_name = 'region'  # Example: 'us-west-2'

# Now, use these credentials to set up your Kinesis client
kinesis_client = boto3.client(
    'kinesis',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

STREAM_NAME = 'example_stream_book'  # Replace with your Kinesis stream name
OPENWEATHERMAP_API_KEY = 'key'  # Replace with your API key
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'

cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]

def get_weather_data(city):
    """Fetch weather data for a city."""
    url = WEATHER_API_URL.format(city, OPENWEATHERMAP_API_KEY)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {city}. Reason: {response.text}")
        return None

def send_data_to_kinesis(data):
    """Send data to Kinesis stream."""
    payload = json.dumps(data)
    print(f"Sending payload: {payload}")
    
    # Put the data record into the Kinesis stream
    kinesis_client.put_record(
        StreamName=STREAM_NAME,
        Data=payload,
        PartitionKey=str(data['id'])  # Using city's weather 'id' as the partition key
    )

if __name__ == "__main__":
    for city in cities:
        data = get_weather_data(city)
        if data:
            send_data_to_kinesis(data)
        time.sleep(5)  # Introducing a short delay to not hit API rate limits and pace the inserts
