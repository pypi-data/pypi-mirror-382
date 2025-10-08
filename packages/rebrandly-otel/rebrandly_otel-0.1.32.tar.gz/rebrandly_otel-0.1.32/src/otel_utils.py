
# otel_utils.py

import os
import sys
import grpc
import json

from opentelemetry.sdk.resources import Resource, SERVICE_NAMESPACE
from opentelemetry.semconv.attributes import service_attributes
from opentelemetry.semconv._incubating.attributes import process_attributes, deployment_attributes

def create_resource(name: str = None, version: str = None) -> Resource:

    if name is None:
        name = get_service_name()
    if version is None:
        version = get_service_version()

    resource = Resource.create(
        {
            service_attributes.SERVICE_NAME: name,
            service_attributes.SERVICE_VERSION: version,
            process_attributes.PROCESS_RUNTIME_VERSION: f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            SERVICE_NAMESPACE: os.environ.get('ENV', os.environ.get('ENVIRONMENT', os.environ.get('NODE_ENV', 'local')))
        }
    )
    return resource

def get_package_version():
    try:
        from importlib.metadata import version, PackageNotFoundError  # Python 3.8+
        return version('rebrandly_otel')
    except ImportError:
        try:
            from importlib_metadata import version, PackageNotFoundError
            return version('rebrandly_otel')
        except Exception as e:
            print(f"[OTEL Utils] Warning: Could not get package version: {e}")
            return '0.1.0'


def get_service_name(service_name: str = None) -> str:
    if service_name is None:
        serv = os.environ.get('OTEL_SERVICE_NAME', 'default-service-python')
        if serv.strip() == "":
            return 'default-service-python'
        return serv
    return service_name


def get_service_version(service_version: str = None) -> str:
    if service_version is None:
        return os.environ.get('OTEL_SERVICE_VERSION', get_package_version())
    return service_version


def get_otlp_endpoint(otlp_endpoint: str = None) -> str | None:
    endpoint = otlp_endpoint or os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT', None)

    if endpoint is not None:

        if endpoint.strip() == "":
            return None

        try:
            from urllib.parse import urlparse

            # Parse the endpoint
            parsed = urlparse(endpoint if '://' in endpoint else f'http://{endpoint}')
            host = parsed.hostname
            port = parsed.port

            # Test gRPC connection
            channel = grpc.insecure_channel(f'{host}:{port}')
            try:
                # Wait for the channel to be ready
                grpc.channel_ready_future(channel).result(timeout=3)
                return endpoint
            finally:
                channel.close()

        except Exception as e:
            print(f"[OTEL] Failed to connect to OTLP endpoint {endpoint}: {e}")
            return None
    return endpoint

def is_otel_debug() -> bool:
    return os.environ.get('OTEL_DEBUG', 'false').lower() == 'true'


def get_millis_batch_time():
    try:
        return int(os.environ.get('BATCH_EXPORT_TIME_MILLIS', 100))
    except Exception as e:
        print(f"[OTEL Utils] Warning: Invalid BATCH_EXPORT_TIME_MILLIS value, using default 5000ms: {e}")
        return 5000

def extract_event_from(message) -> str | None:
    body = None
    if 'body' in message:
        body = message['body']
    if 'Body' in message:
        body = message['Body']
    if 'Message' in message:
        body = message['Message']
    if 'Sns' in message and 'Message' in message['Sns']:
        body = message['Sns']['Message']
    if body is not None:
        try:
            jbody = json.loads(body)
            if 'event' in jbody:
                return jbody['event']
        except:
            pass
    return None