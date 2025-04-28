# test_kafka_s3_consumer.py
import unittest
from unittest.mock import patch, MagicMock, call
import json
import time
import threading
from io import BytesIO
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from confluent_kafka import Consumer
from kafkaconsumer.kafkaconsumer import (
    convert_to_parquet,
    upload_to_s3,
    consume_messages,
    TOPIC_LIST,
    BATCH_SIZE,
    UPLOAD_INTERVAL
)


class TestKafkaS3Consumer(unittest.TestCase):
    def setUp(self):
        # Sample test data
        self.sample_message = {
            "timestamp": "2023-01-01T08:00:00",
            "location": "Mcloed Ganj",
            "vehicle_count": "150",
            "avg_speed_kmph": "45.5",
            "congestion_level": "moderate",
            "weather": "sunny",
            "accidents_reported": "1"
        }
        self.encoded_message = json.dumps(self.sample_message).encode('utf-8')

    def test_convert_to_parquet(self):
        # Test data conversion
        data = [self.sample_message]
        parquet_data = convert_to_parquet(data)

        # Verify we get bytes back
        self.assertIsInstance(parquet_data, bytes)

        # Verify we can read the parquet data
        table = pq.read_table(BytesIO(parquet_data))
        df = table.to_pandas()
        self.assertEqual(df.iloc[0]['location'], "Mcloed Ganj")

    @patch('your_module.s3_client.put_object')
    def test_upload_to_s3_success(self, mock_put):
        # Test successful S3 upload
        data = [self.sample_message]
        topic = "test-topic"

        upload_to_s3(data, topic)

        # Verify put_object was called
        mock_put.assert_called_once()
        args, kwargs = mock_put.call_args
        self.assertEqual(kwargs['Bucket'], "citystream-traffic")
        self.assertTrue(kwargs['Key'].startswith("traffic_data/test-topic_"))
        self.assertTrue(kwargs['Key'].endswith(".parquet"))

    @patch('your_module.s3_client.put_object')
    @patch('your_module.print')
    def test_upload_to_s3_failure(self, mock_print, mock_put):
        # Test failed S3 upload
        mock_put.side_effect = Exception("S3 Error")
        data = [self.sample_message]
        topic = "test-topic"

        upload_to_s3(data, topic)

        # Verify error was handled
        mock_print.assert_called_with(" S3 Upload Failed: S3 Error")

    @patch('your_module.Consumer')
    @patch('your_module.upload_to_s3')
    @patch('your_module.time.time')
    def test_consume_messages_batch_size(self, mock_time, mock_upload, mock_consumer):
        # Test batch size triggering upload
        mock_time.return_value = 1000
        mock_consumer_instance = MagicMock()
        mock_consumer.return_value = mock_consumer_instance

        # Setup mock messages
        messages = [MagicMock() for _ in range(BATCH_SIZE)]
        for msg in messages:
            msg.error.return_value = None
            msg.value.return_value = self.encoded_message

        mock_consumer_instance.poll.side_effect = messages + [None]

        # Run consumer
        consume_messages("test-topic")

        # Verify upload was triggered by batch size
        mock_upload.assert_called_once()
        self.assertEqual(len(mock_upload.call_args[0][0]), BATCH_SIZE)

    @patch('your_module.Consumer')
    @patch('your_module.upload_to_s3')
    @patch('your_module.time.time')
    def test_consume_messages_time_interval(self, mock_time, mock_upload, mock_consumer):
        # Test time interval triggering upload
        mock_time.side_effect = [1000, 1000 + UPLOAD_INTERVAL - 1, 1000 + UPLOAD_INTERVAL + 1]
        mock_consumer_instance = MagicMock()
        mock_consumer.return_value = mock_consumer_instance

        # Setup mock messages
        msg = MagicMock()
        msg.error.return_value = None
        msg.value.return_value = self.encoded_message
        mock_consumer_instance.poll.side_effect = [msg, None]

        # Run consumer
        consume_messages("test-topic")

        # Verify upload was triggered by time interval
        mock_upload.assert_called_once()

    @patch('your_module.threading.Thread')
    @patch('your_module.consume_messages')
    def test_main_thread_creation(self, mock_consume, mock_thread):
        # Test that threads are created for each topic
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Import and run the main block
        with patch('__main__.__name__', '__main__'):
            import your_module  # This will execute the thread creation code

        # Verify threads were created for each topic
        self.assertEqual(mock_thread.call_count, len(TOPIC_LIST))
        self.assertEqual(mock_thread_instance.start.call_count, len(TOPIC_LIST))

    @patch('your_module.Consumer')
    def test_consumer_error_handling(self, mock_consumer):
        # Test consumer error handling
        mock_consumer_instance = MagicMock()
        mock_consumer.return_value = mock_consumer_instance

        # Setup error message
        error_msg = MagicMock()
        error_msg.error.return_value = "Test Error"
        mock_consumer_instance.poll.side_effect = [error_msg, None]

        # Run consumer
        consume_messages("test-topic")

        # Verify error was handled (you might want to add logging verification)


if __name__ == '__main__':
    unittest.main()