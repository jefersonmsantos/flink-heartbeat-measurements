import os
import argparse
import base64
import logging
import sys
import json
from typing import Iterable, Tuple as pyTuple, Dict
import datetime
import time
import google.auth
import google.auth.transport.urllib3
import urllib3
from dotenv import load_dotenv

from pyflink.common import WatermarkStrategy, Time, Types, Row, Duration
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors import KafkaSource
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.functions import ProcessWindowFunction, MapFunction
from pyflink.datastream.window import TumblingEventTimeWindows

from google.cloud import bigquery_storage_v1
from google.cloud.bigquery_storage_v1 import types, writer
from google.protobuf import descriptor_pb2

import sample_data_pb2


class BigqueryStorageApiClient:
    def __init__(self, project_id, dataset_id, table_id):
        self.write_client = bigquery_storage_v1.BigQueryWriteClient()
        self.parent = self.write_client.table_path(project_id, dataset_id, table_id)
        self.stream_name = f'{self.parent}/_default'
        #write_stream = types.WriteStream()
 
        # Create a template with fields needed for the first request.
        self.request_template = types.AppendRowsRequest()
 
        # The request must contain the stream name.
        self.request_template.write_stream = self.stream_name
 
        # So that BigQuery knows how to parse the serialized_rows, generate a
        # protocol buffer representation of your message descriptor.
        self.proto_schema = types.ProtoSchema()
        self.proto_descriptor = descriptor_pb2.DescriptorProto()
        sample_data_pb2.SampleData.DESCRIPTOR.CopyToProto(self.proto_descriptor)
        self.proto_schema.proto_descriptor = self.proto_descriptor
        self.proto_data = types.AppendRowsRequest.ProtoData()
        self.proto_data.writer_schema = self.proto_schema
        self.request_template.proto_rows = self.proto_data
 
        # Some stream types support an unbounded number of requests. Construct an
        # AppendRowsStream to send an arbitrary number of requests to a stream.
        self.append_rows_stream = writer.AppendRowsStream(self.write_client, self.request_template)
 
        # Calls the create_row_data function to append proto2 serialized bytes to the
        # serialized_rows repeated field.
        self.proto_rows = types.ProtoRows()

    def write_row(self, row):
        proto_rows = types.ProtoRows()
        proto_rows.serialized_rows.append(self.create_row_data(row))

        request = types.AppendRowsRequest()
        proto_data = types.AppendRowsRequest.ProtoData()
        proto_data.rows = proto_rows
        request.proto_rows = proto_data
 
        self.append_rows_stream.send(request)
        print(f"Rows to table: '{self.parent}' have been written.")
    

    @staticmethod
    def create_row_data(data):
        row = sample_data_pb2.SampleData()
        FIELDS_TO_CHECK = [
        "window_start",
        "window_end",
        "key",
        "total",
        "count",
        "avg",
        "_CHANGE_TYPE"]

        for field in FIELDS_TO_CHECK:
        # This IF statement is particularly useful when optional fields aren't provided and thus are passed
        # as null values to BigQuery.
            if field in data:
                setattr(row, field, data[field])
        #setattr(row, "_CHANGE_TYPE", "UPSERT")
        return row.SerializeToString()

class BigQueryRichMapFunction(MapFunction):
    def open(self, runtime_context):
        # Initialize the BigQuery client in the open method to avoid serialization issues
        self.bq_storage_client = BigqueryStorageApiClient(
            project_id="edc-igti-325912",
            dataset_id="measurements",
            table_id="heartbeat_average"
        )

    def map(self, value):
        # Write each row to BigQuery
        print(value)
        self.bq_storage_client.write_row(value)
        return value

class MyTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, element: dict, record_timestamp: int) -> int:
        dt=datetime.fromisoformat(element['occurred_at'])
        return int(dt.timestamp()*1000)

class MyProcessWindowFunction(ProcessWindowFunction):

    def process(self, key: str, context: ProcessWindowFunction.Context,
                elements: Iterable[Dict]) -> Iterable[Dict]:
        count = 0
        for _ in elements:
            count += 1
        total_heartbeat = sum(e["heartbeat"] for e in elements)
        avg = float(total_heartbeat/count)
        #yield "Window: {} State: {} Total: {} count: {} average: {}".format(context.window(), key, total_heartbeat, count, avg)
        yield {
            "window_start":context.window().start
            , "window_end":context.window().end
            , "key": key
            , "total": total_heartbeat
            , "count":count
            , "avg":avg
        }

def process_measurements(input_topic, bootstrap_server, username, password):
    print('start')
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    # write all the data to one file
    env.set_parallelism(1)

    dirname = os.path.dirname(__file__)

    env.add_jars(f"file://{os.path.join(dirname, 'flink-sql-connector-kafka-3.2.0-1.19.jar')}",f"file://{os.path.join(dirname, 'kafka-clients-3.7.1.jar')}")


    properties = {
        'bootstrap.servers': bootstrap_server,
        'sasl.mechanism': 'PLAIN',
        'security.protocol': 'SASL_SSL',
        'sasl.jaas.config': f"org.apache.kafka.common.security.plain.PlainLoginModule required \
                            username='{username}' \
                            password='{password}';",
    }

    source = KafkaSource.builder() \
        .set_properties(properties) \
        .set_topics(input_topic) \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    ds = env.from_source(source
                         , WatermarkStrategy
                            .for_bounded_out_of_orderness(Duration.of_seconds(10))
                            .with_timestamp_assigner(MyTimestampAssigner())
                         , "Measurements Source")


    processed_ds = ds.map(lambda v: json.loads(v)) \
        .key_by(lambda v: v["state"]) \
        .window(TumblingEventTimeWindows.of(Time.seconds(2))) \
        .process(MyProcessWindowFunction()) \
        .map(lambda v: {**v, "_CHANGE_TYPE": "UPSERT"}) 

    # Use the output function to write to BigQuery
    processed_ds.map(BigQueryRichMapFunction())
    
    env.execute()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_topic',
        dest='input_topic',
        required=False,
        help='Input topic to process.')
    
    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)

    load_dotenv()

    bootstrap_server = os.getenv('BOOTSTRAP_SERVER')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    process_measurements(known_args.input_topic, bootstrap_server, username, password)