"""
Open Telemetry integration in a Django project.

The primary export of this module is :func:`setup_otel`, which is intended to be called
from the ``setup_env`` function in projects.

The Python OpenTelemetry SDK supports the standardized environment variables,
see the `environment variables reference`_.

We define one custom environment variable ``_OTEL_ENABLE_CONTAINER_RESOURCE_DETECTOR``
to opt-in to container resource detection when the application is being deployed on a
non-kubernetes container runtime (such as Docker or Podman).

.. _`environment variables reference`: https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/
"""

import os
from typing import Literal, assert_never
from uuid import uuid4

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from opentelemetry import metrics, trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.environment_variables import OTEL_EXPORTER_OTLP_PROTOCOL
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_INSTANCE_ID,
    SERVICE_VERSION,
    Resource,
    get_aggregated_resources,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from maykin_common.settings import get_setting

# the uwsgi module is special - it's only available when the python code is loaded
# through uwsgi. With regular ``manage.py`` usage, it does not exist.
try:
    import uwsgi  # pyright: ignore[reportMissingModuleSource] uwsgi magic...
except ImportError:
    uwsgi = None

__all__ = [
    "setup_otel",
]

# The Python SDK only supports gRPC and HTTP/protobuf. HTTP/json is not supported.
type ExportProtocol = Literal["grpc", "http/protobuf"]

DEFAULT_PROTOCOL: ExportProtocol = "grpc"


def setup_otel() -> None:
    """
    Initialize the Open Telemetry machinery.

    This is an application-global hook to configure the Open Telemetry machinery:

    * set up the metadata about the resource being monitored
    * initialize the metrics processor and exporter
    * initialize the traces processor and exporter
    * instrument the python code so that metrics and traces are captured

    The exports are responsible for shipping the telemetry data to an endpoint that
    supports OpenTelemetryProtocol (OTLP), either over gRPC or HTTP/protobuf protocols.
    Often, this will be an OpenTelemetry Collector running somewhere.

    Part of the SDK initialization process is starting a background thread to
    periodically ship the telemetry to the configured endpoint.
    """
    # set up instrumenters that (usually) monkeypatch modules or inject the right
    # wrappers/middleware etc.

    # the instrumentor is a singleton, so it's effectively global
    instrumentor = DjangoInstrumentor()
    if not instrumentor.is_instrumented_by_opentelemetry:
        instrumentor.instrument()

    # In some situations (similar to uwsgi, see below), initialization must be deferred,
    # e.g. in celery workers with a process pool that fork other processes. Detecting
    # if we're running in a celery master or worker process is not obvious, so instead
    # we look at an explicit environment variable.
    defer_setup = _check_envvar("_OTEL_DEFER_SETUP", default="false")

    # in a uwsgi worker, defer the otel initialization until after the processes have
    # forked
    if uwsgi is not None:  # pragma: no cover - can't be tested outside of uwsgi
        from uwsgidecorators import postfork

        postfork(_setup_otel)
    elif not defer_setup:
        _setup_otel()

    # similar to uwsgi postfork, bind a handler when a worker process has initialized
    try:
        worker_process_init = import_string("celery.signals.worker_process_init")
        worker_process_init.connect(weak=False)(lambda *args, **kwargs: _setup_otel())
    # Celery is an optional dependency
    except ImportError:
        pass


def _setup_otel() -> None:
    """
    Helper function for the actual initialization.

    This helpers makes it possible to actually properly initialize in a non-uwsgi
    context, while deferring the initialization until post-fork in a uwsgi context.
    """
    _already_initialized = isinstance(trace.get_tracer_provider(), TracerProvider)
    if _already_initialized:
        return

    if "OTEL_SERVICE_NAME" not in os.environ:
        raise ImproperlyConfigured(
            "You must define the 'OTEL_SERVICE_NAME' environment variable."
        )
    # the service name now is guaranteed to be set through envvars
    resource = Resource.create(
        attributes={
            SERVICE_VERSION: get_setting("RELEASE") or "",
            SERVICE_INSTANCE_ID: str(uuid4()),
            DEPLOYMENT_ENVIRONMENT: get_setting("ENVIRONMENT") or "",
        }
    )
    resource = aggregate_resource(resource)

    OTLPMetricExporter, OTLPSpanExporter = load_exporters()

    tracer_provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter())
    tracer_provider.add_span_processor(processor)
    trace.set_tracer_provider(tracer_provider)

    reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)


def load_exporters():
    # TODO: replace with `config` helper once it's added to this library
    protocol: ExportProtocol = os.getenv(  # pyright: ignore[reportAssignmentType]
        OTEL_EXPORTER_OTLP_PROTOCOL, default=DEFAULT_PROTOCOL
    )
    match protocol:
        case "grpc":
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
                OTLPMetricExporter,
            )
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            return (OTLPMetricExporter, OTLPSpanExporter)
        case "http/protobuf":
            from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
                OTLPMetricExporter,
            )
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            return (OTLPMetricExporter, OTLPSpanExporter)
        case _:
            assert_never(protocol)


def aggregate_resource(resource: Resource) -> Resource:
    # TODO: replace with `config` helper once it's added to this library
    _enable_resource_detector = _check_envvar(
        "_OTEL_ENABLE_CONTAINER_RESOURCE_DETECTOR", default="false"
    )
    if not _enable_resource_detector:
        return resource

    from opentelemetry.resource.detector.containerid import ContainerResourceDetector

    return get_aggregated_resources(
        detectors=[ContainerResourceDetector()], initial_resource=resource
    )


def _check_envvar(name: str, default: Literal["true", "false"]) -> bool:
    return os.getenv(name, default=default).lower().strip() == "true"
