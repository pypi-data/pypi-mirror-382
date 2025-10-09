import json
import logging
from dotenv import load_dotenv
import os
import pytest
from datetime import datetime, timedelta, timezone

from cc_clients_python_lib.http_status import HttpStatus
from cc_clients_python_lib.metrics_client import MetricsClient, METRICS_CONFIG, KafkaMetric, DataMovementType


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"
 

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize the global variables.
metrics_config = {}
kafka_cluster_id = ""
kafka_topic_name = ""
query_start_time = ""
query_end_time = ""


@pytest.fixture(autouse=True)
def load_configurations():
    """Load the Metrics configuration and Kafka test topic from the environment variables."""
    load_dotenv()
 
    
    # Set the Metrics configuration.
    global metrics_config
    metrics_config[METRICS_CONFIG["confluent_cloud_api_key"]] = os.getenv("CONFLUENT_CLOUD_API_KEY")
    metrics_config[METRICS_CONFIG["confluent_cloud_api_secret"]] = os.getenv("CONFLUENT_CLOUD_API_SECRET")

    global kafka_cluster_id
    global kafka_topic_name
    global query_start_time
    global query_end_time

    # Set the Kafka test topic.
    kafka_topic_name = os.getenv("KAFKA_TOPIC_NAME")
    kafka_cluster_id = os.getenv("KAFKA_CLUSTER_ID")


def test_get_topic_received_total_bytes():
    """Test the get_topic_total() function for getting the total bytes."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    # Calculate the ISO 8601 formatted start and end times within a rolling window for the last 1 day
    utc_now = datetime.now(timezone.utc)
    seven_days_ago = utc_now - timedelta(days=1)
    iso_start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
    iso_end_time = utc_now.strftime('%Y-%m-%dT%H:%M:%S')

    query_start_time =  datetime.fromisoformat(iso_start_time.replace('Z', '+00:00'))
    query_end_time = datetime.fromisoformat(iso_end_time.replace('Z', '+00:00'))

    http_status_code, error_message, rate_limits, query_result = metrics_client.get_topic_total(KafkaMetric.RECEIVED_BYTES, kafka_cluster_id, kafka_topic_name, query_start_time, query_end_time)

    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified_result = json.dumps(query_result, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, beautified_rate_limits, beautified_result)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, rate_limits, query_result)
    

def test_get_topic_received_total_records():
    """Test the get_topic_total() function for getting the total records."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    # Calculate the ISO 8601 formatted start and end times within a rolling window for the last 1 day
    utc_now = datetime.now(timezone.utc)
    seven_days_ago = utc_now - timedelta(days=1)
    iso_start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
    iso_end_time = utc_now.strftime('%Y-%m-%dT%H:%M:%S')

    query_start_time =  datetime.fromisoformat(iso_start_time.replace('Z', '+00:00'))
    query_end_time = datetime.fromisoformat(iso_end_time.replace('Z', '+00:00'))

    http_status_code, error_message, rate_limits, query_result = metrics_client.get_topic_total(KafkaMetric.RECEIVED_RECORDS, kafka_cluster_id, kafka_topic_name, query_start_time, query_end_time)
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified_result = json.dumps(query_result, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, beautified_rate_limits, beautified_result)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, rate_limits, query_result)


def test_get_topic_received_daily_aggregated_totals_bytes():
    """Test the get_topic_daily_aggregated_totals() function for getting the daily aggregated totals bytes."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    http_status_code, error_message, rate_limits, query_result = metrics_client.get_topic_daily_aggregated_totals(KafkaMetric.RECEIVED_BYTES, kafka_cluster_id, kafka_topic_name)
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
        
        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified_result = json.dumps(query_result, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, beautified_rate_limits, beautified_result)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, rate_limits, query_result)

def test_get_topic_received_daily_aggregated_totals_records():
    """Test the get_topic_daily_aggregated_totals() function for getting the daily aggregated totals records."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    http_status_code, error_message, rate_limits, query_result = metrics_client.get_topic_daily_aggregated_totals(KafkaMetric.RECEIVED_RECORDS, kafka_cluster_id, kafka_topic_name)
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"


        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified_result = json.dumps(query_result, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, beautified_rate_limits, beautified_result)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, rate_limits, query_result)


def test_compute_topic_partition_count_based_on_received_bytes_record_count():
    """Test computing the recommended partition count based on received bytes and record count."""
                
    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)
    
    http_status_code, error_message, _, bytes_query_result = metrics_client.get_topic_daily_aggregated_totals(KafkaMetric.RECEIVED_BYTES, kafka_cluster_id, kafka_topic_name)
    
    try:
        assert http_status_code == HttpStatus.OK, f"Received Bytes call -HTTP Status Code: {http_status_code}"

        bytes_daily_totals = bytes_query_result.get('daily_total', [])
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, bytes_query_result)
        return

    http_status_code, error_message, _, record_query_result = metrics_client.get_topic_daily_aggregated_totals(KafkaMetric.RECEIVED_RECORDS, kafka_cluster_id, kafka_topic_name)

    try:
        assert http_status_code == HttpStatus.OK, f"Received Records call - HTTP Status Code: {http_status_code}"

        required_consumption_throughput_factor = 3

        record_count = record_query_result.get('sum_total', 0)

        records_daily_totals = record_query_result.get('daily_total', [])
        avg_bytes_daily_totals = []

        for index, record_total in enumerate(records_daily_totals):
            if record_total:
                avg_bytes_daily_totals.append(bytes_daily_totals[index]/record_total)

        avg_bytes_per_record = sum(avg_bytes_daily_totals)/len(avg_bytes_daily_totals) if len(avg_bytes_daily_totals) > 0 else 0

        logging.info("Confluent Metrics API - For topic %s, the average bytes per record is %.2f bytes/record for a total of %.0f records.", kafka_topic_name, avg_bytes_per_record, record_count)

        # Calculate consumer throughput and required throughput
        consumer_throughput = avg_bytes_per_record * record_count
        required_throughput = consumer_throughput * required_consumption_throughput_factor
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, record_query_result)
        return

    # Calculate recommended partition count
    recommended_partition_count = round(required_throughput / consumer_throughput)

    logger.info("Confluent Metrics API - For topic %s, the recommended partition count is %d partitions to support a required consumption throughput of %.2f bytes/second.", kafka_topic_name, recommended_partition_count, required_throughput)


def test_get_topic_sent_total_bytes():
    """Test the get_topic_total() function for getting the total bytes."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    # Calculate the ISO 8601 formatted start and end times within a rolling window for the last 1 day
    utc_now = datetime.now(timezone.utc)
    seven_days_ago = utc_now - timedelta(days=1)
    iso_start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
    iso_end_time = utc_now.strftime('%Y-%m-%dT%H:%M:%S')

    query_start_time =  datetime.fromisoformat(iso_start_time.replace('Z', '+00:00'))
    query_end_time = datetime.fromisoformat(iso_end_time.replace('Z', '+00:00'))

    http_status_code, error_message, rate_limits, query_result = metrics_client.get_topic_total(KafkaMetric.SENT_BYTES, kafka_cluster_id, kafka_topic_name, query_start_time, query_end_time)

    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified_result = json.dumps(query_result, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, beautified_rate_limits, beautified_result)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, rate_limits, query_result)
    

def test_get_topic_sent_total_records():
    """Test the get_topic_total() function for getting the total records."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    # Calculate the ISO 8601 formatted start and end times within a rolling window for the last 1 day
    utc_now = datetime.now(timezone.utc)
    seven_days_ago = utc_now - timedelta(days=1)
    iso_start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
    iso_end_time = utc_now.strftime('%Y-%m-%dT%H:%M:%S')

    query_start_time =  datetime.fromisoformat(iso_start_time.replace('Z', '+00:00'))
    query_end_time = datetime.fromisoformat(iso_end_time.replace('Z', '+00:00'))

    http_status_code, error_message, rate_limits, query_result = metrics_client.get_topic_total(KafkaMetric.SENT_RECORDS, kafka_cluster_id, kafka_topic_name, query_start_time, query_end_time)
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified_result = json.dumps(query_result, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, beautified_rate_limits, beautified_result)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, rate_limits, query_result)


def test_get_topic_sent_daily_aggregated_totals_bytes():
    """Test the get_topic_daily_aggregated_totals() function for getting the daily aggregated totals bytes."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    http_status_code, error_message, rate_limits, query_result = metrics_client.get_topic_daily_aggregated_totals(KafkaMetric.SENT_BYTES, kafka_cluster_id, kafka_topic_name)

    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"
        
        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified_result = json.dumps(query_result, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, beautified_rate_limits, beautified_result)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, rate_limits, query_result)
    

def test_get_topic_sent_daily_aggregated_totals_records():
    """Test the get_topic_daily_aggregated_totals() function for getting the daily aggregated totals records."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    http_status_code, error_message, rate_limits, query_result = metrics_client.get_topic_daily_aggregated_totals(KafkaMetric.SENT_RECORDS, kafka_cluster_id, kafka_topic_name)
 
    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified_result = json.dumps(query_result, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, beautified_rate_limits, beautified_result)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, rate_limits: %s, Query Result: %s", http_status_code, error_message, rate_limits, query_result)


def test_compute_topic_partition_count_based_on_sent_bytes_record_count():
    """Test computing the recommended partition count based on sent bytes and record count."""
                
    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    http_status_code, error_message, _, bytes_query_result = metrics_client.get_topic_daily_aggregated_totals(KafkaMetric.SENT_BYTES, kafka_cluster_id, kafka_topic_name)

    
    try:
        assert http_status_code == HttpStatus.OK, f"Sent Bytes call -HTTP Status Code: {http_status_code}"

        bytes_daily_totals = bytes_query_result.get('daily_total', [])
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, bytes_query_result)
        return

    http_status_code, error_message, _, record_query_result = metrics_client.get_topic_daily_aggregated_totals(KafkaMetric.SENT_RECORDS, kafka_cluster_id, kafka_topic_name)

    try:
        assert http_status_code == HttpStatus.OK, f"Sent Records call - HTTP Status Code: {http_status_code}"

        required_consumption_throughput_factor = 3

        record_count = record_query_result.get('sum_total', 0)

        records_daily_totals = record_query_result.get('daily_total', [])
        avg_bytes_daily_totals = []

        for index, record_total in enumerate(records_daily_totals):
            if record_total:
                avg_bytes_daily_totals.append(bytes_daily_totals[index]/record_total)

        avg_bytes_per_record = sum(avg_bytes_daily_totals)/len(avg_bytes_daily_totals) if len(avg_bytes_daily_totals) > 0 else 0

        logging.info("Confluent Metrics API - For topic %s, the average bytes per record is %.2f bytes/record for a total of %.0f records.", kafka_topic_name, avg_bytes_per_record, record_count)

        # Calculate consumer throughput and required throughput
        consumer_throughput = avg_bytes_per_record * record_count
        required_throughput = consumer_throughput * required_consumption_throughput_factor
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Query Result: %s", http_status_code, error_message, record_query_result)
        return

    # Calculate recommended partition count
    recommended_partition_count = round(required_throughput / consumer_throughput)

    logger.info("Confluent Metrics API - For topic %s, the recommended partition count is %d partitions to support a required consumption throughput of %.2f bytes/second.", kafka_topic_name, recommended_partition_count, required_throughput)

def test_is_topic_partition_hot_by_ingress_throughput():
    """Test the is_topic_partition_hot() function for checking if a topic partition is hot
    by ingress throughput."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    # Calculate the ISO 8601 formatted start and end times within a rolling window for the last 1 day
    utc_now = datetime.now(timezone.utc)
    seven_days_ago = utc_now - timedelta(days=1)
    iso_start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
    iso_end_time = utc_now.strftime('%Y-%m-%dT%H:%M:%S')

    query_start_time =  datetime.fromisoformat(iso_start_time.replace('Z', '+00:00'))
    query_end_time = datetime.fromisoformat(iso_end_time.replace('Z', '+00:00'))

    http_status_code, error_message, rate_limits, is_partition_hot = metrics_client.is_topic_partition_hot(kafka_cluster_id, kafka_topic_name, DataMovementType.INGRESS, query_start_time, query_end_time)

    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified = json.dumps(is_partition_hot, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, Rate Limits: %s, Is Partition Hot: %s", http_status_code, error_message, beautified_rate_limits, beautified)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Rate Limits: %s, Is Partition Hot: %s", http_status_code, error_message, rate_limits, is_partition_hot)

def test_is_topic_partition_hot_by_egress_throughput():
    """Test the is_topic_partition_hot() function for checking if a topic partition is hot
    by egress throughput."""

    # Instantiate the MetricsClient class.
    metrics_client = MetricsClient(metrics_config)

    # Calculate the ISO 8601 formatted start and end times within a rolling window for the last 1 day
    utc_now = datetime.now(timezone.utc)
    seven_days_ago = utc_now - timedelta(days=1)
    iso_start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
    iso_end_time = utc_now.strftime('%Y-%m-%dT%H:%M:%S')

    query_start_time =  datetime.fromisoformat(iso_start_time.replace('Z', '+00:00'))
    query_end_time = datetime.fromisoformat(iso_end_time.replace('Z', '+00:00'))

    http_status_code, error_message, rate_limits, is_partition_hot = metrics_client.is_topic_partition_hot(kafka_cluster_id, kafka_topic_name, DataMovementType.EGRESS, query_start_time, query_end_time)

    try:
        assert http_status_code == HttpStatus.OK, f"HTTP Status Code: {http_status_code}"

        beautified_rate_limits = json.dumps(rate_limits, indent=4, sort_keys=True)
        beautified = json.dumps(is_partition_hot, indent=4, sort_keys=True)
        logger.info("HTTP Status Code: %d, Error Message: %s, Rate Limits: %s, Is Partition Hot: %s", http_status_code, error_message, beautified_rate_limits, beautified)
    except AssertionError as e:
        logger.error(e)
        logger.error("HTTP Status Code: %d, Error Message: %s, Rate Limits: %s, Is Partition Hot: %s", http_status_code, error_message, beautified_rate_limits, beautified)