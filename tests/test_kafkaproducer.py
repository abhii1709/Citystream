# test_kafka_producer.py
import unittest
from unittest.mock import patch, MagicMock
import json
import threading
from kafkaproducer.kafkaproducer import (
    locations,
    API_URL,
    PAGE_SIZE,
    NUM_THREADS,
    producer_config,
    fetch_page,
    process_and_publish,
    start_producer,
    delivery_report
)


class TestKafkaProducer(unittest.TestCase):
    def setUp(self):
        # Sample test data
        self.sample_record = {
            "timestamp": "2023-01-01T08:00:00",
            "location": "Mcloed Ganj",
            "vehicle_count": "150",
            "avg_speed_kmph": "45.5",
            "congestion_level": "moderate",
            "weather": "sunny",
            "accidents_reported": "1"
        }
        self.sample_response = [self.sample_record]

    @patch('requests.get')
    def test_fetch_page_success(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_response
        mock_get.return_value = mock_response

        result = fetch_page(1)
        self.assertEqual(result, self.sample_response)
        mock_get.assert_called_once_with(
            API_URL,
            params={"page": 1, "size": PAGE_SIZE}
        )

    @patch('requests.get')
    def test_fetch_page_failure(self, mock_get):
        # Mock failed API response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = fetch_page(1)
        self.assertEqual(result, [])
        mock_get.assert_called_once()

    def test_delivery_report_success(self):
        # Test successful delivery report
        mock_msg = MagicMock()
        mock_msg.topic.return_value = "test_topic"
        mock_msg.partition.return_value = 0
        delivery_report(None, mock_msg)  # Should print success message

    def test_delivery_report_failure(self):
        # Test failed delivery report
        mock_err = MagicMock()
        mock_err.str.return_value = "Test error"
        delivery_report(mock_err, None)  # Should print error message

    @patch('kafka_producer.fetch_page')
    @patch('kafka_producer.Producer')
    def test_process_and_publish(self, mock_producer, mock_fetch):
        # Setup mocks
        mock_fetch.return_value = self.sample_response
        mock_prod_instance = MagicMock()
        mock_producer.return_value = mock_prod_instance

        # Call the function
        process_and_publish(1)

        # Verify behavior
        mock_fetch.assert_called_once_with(1)
        mock_producer.assert_called_once_with(producer_config)

        # Verify producer was called with correct arguments
        expected_topic = locations[self.sample_record['location']]
        expected_key = self.sample_record['location'].encode('utf-8')
        expected_value = json.dumps(self.sample_record).encode('utf-8')

        mock_prod_instance.produce.assert_called_once_with(
            expected_topic,
            key=expected_key,
            value=expected_value,
            callback=delivery_report
        )
        mock_prod_instance.flush.assert_called_once()

    @patch('kafka_producer.process_and_publish')
    @patch('kafka_producer.threading.Thread')
    def test_start_producer(self, mock_thread, mock_process):
        # Setup mocks
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Call the function
        start_producer()

        # Verify behavior
        self.assertEqual(mock_thread.call_count, NUM_THREADS)
        self.assertEqual(mock_thread_instance.start.call_count, NUM_THREADS)
        self.assertEqual(mock_thread_instance.join.call_count, NUM_THREADS)

        # Verify correct page numbers were used
        expected_calls = [unittest.mock.call(args=(i + 1,)) for i in range(NUM_THREADS)]
        mock_process.assert_has_calls(expected_calls, any_order=True)

    @patch('kafka_producer.process_and_publish')
    @patch('kafka_producer.threading.Thread')
    def test_start_producer_with_no_location_match(self, mock_thread, mock_process):
        # Test with data that doesn't match any location
        test_data = [{
            "timestamp": "2023-01-01T08:00:00",
            "location": "Unknown Location",
            "vehicle_count": "150",
            "avg_speed_kmph": "45.5",
            "congestion_level": "moderate",
            "weather": "sunny",
            "accidents_reported": "1"
        }]

        with patch('kafka_producer.fetch_page', return_value=test_data):
            with patch('kafka_producer.Producer') as mock_producer:
                mock_prod_instance = MagicMock()
                mock_producer.return_value = mock_prod_instance

                process_and_publish(1)

                # Verify no messages were produced
                mock_prod_instance.produce.assert_not_called()
                mock_prod_instance.flush.assert_called_once()


if __name__ == '__main__':
    unittest.main()