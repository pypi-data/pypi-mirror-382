from __future__ import annotations

import functools
import inspect
import sys
import traceback
from copy import copy
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Sequence

from django.db import connection
from django.db import transaction as _transaction
from django.http import Http404
from django.http.response import HttpResponseBase
from django.utils.translation import gettext_lazy as _
from drf_spectacular.drainage import get_view_method_names, isolate_view_method
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.fields import empty
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings as drf_api_settings

from drf_apischema.plumbing import any_success, is_action_view, is_not_empty_none, true_empty_str

from .request import ASRequest
from .response import StatusResponse
from .settings import api_settings, with_override
from .utils import HttpError, is_accept_json

_SerializerType = Serializer | type[Serializer]


@dataclass
class ProcessEvent:
    request: ASRequest
    view: Callable | None
    args: tuple
    kwargs: dict

    def get_object(self):
        return self.view.get_object() if self.detail else None  # type: ignore

    @property
    def query_data(self):
        return self.request.GET

    @property
    def body_data(self):
        return self.request.data

    @property
    def detail(self) -> bool:
        return self.view.detail if self.view else False


@dataclass
class ArgCollection:
    raw_func: Any = None
    func: Any = None
    cls: Any = None
    permissions: Iterable[type[BasePermission]] | None = None
    query: Any = None
    body: Any = empty
    response: Any = empty
    responses: Any = empty
    summary: str | None = None
    description: str | None = None
    summary_from_doc: bool | None = None
    tags: Sequence[str] | None = None
    transaction: bool | None = None
    sqllogging: bool | None = None
    deprecated: bool = False

    def override(self, other: ArgCollection):
        self.func = self.func if other.func is None else other.func
        self.cls = self.cls if other.cls is None else other.cls
        # self.permissions = self.permissions if other.permissions is None else other.permissions
        if other.permissions is not None:
            raise ValueError("Permissions cannot be set after the first call")
        # self.query = self.query if other.query is None else other.query
        # self.body = self.body if other.body is empty else other.body
        if other.query is not None:
            raise ValueError("Query cannot be set after the first call")
        if other.body is not empty:
            raise ValueError("Body cannot be set after the first call")
        self.response = self.response if other.response is empty else other.response
        self.responses = self.responses if other.responses is empty else other.responses
        self.summary = self.summary if other.summary is None else other.summary
        self.description = self.description if other.description is None else other.description
        self.tags = self.tags if other.tags is None else other.tags
        # self.transaction = self.transaction if other.transaction is None else other.transaction
        if other.transaction is not None:
            raise ValueError("Transaction cannot be set after the first call")
        # self.sqllogging = self.sqllogging if other.sqllogging is None else other.sqllogging
        if other.sqllogging is not None:
            raise ValueError("Sqllogging cannot be set after the first call")
        self.deprecated = self.deprecated if other.deprecated is None else other.deprecated
        return self


def _wrap_view_method(view, method_name, decorator):
    wrapped = decorator(isolate_view_method(view, method_name), view)
    if wrapped:
        setattr(view, method_name, wrapped)


def apischema_view(**kwargs):
    def decorator(view):
        # special case for @api_view. redirect decoration to enclosed WrappedAPIView
        if callable(view) and hasattr(view, "cls"):
            apischema_view(**kwargs)(view.cls)
            return view

        available_view_methods = get_view_method_names(view)

        for method_name, method_decorator in kwargs.items():
            if method_name not in available_view_methods:
                continue
            _wrap_view_method(view, method_name, method_decorator)
        for method_name in set(available_view_methods).difference(kwargs).difference({"options"}):
            _wrap_view_method(view, method_name, apischema())
        return view

    return decorator


def apischema(
    permissions: Iterable[type[BasePermission]] | None = None,
    query: Any = None,
    parameters: Sequence[OpenApiParameter | _SerializerType] | None = None,
    body: Any = empty,
    response: Any = empty,
    responses: Any = empty,
    summary: str | None = None,
    description: str | None = None,
    summary_from_doc: bool | None = None,
    tags: Sequence[str] | None = None,
    transaction: bool | None = None,
    sqllogging: bool | None = None,
    deprecated: bool = False,
    **kwargs,
) -> Callable[..., Callable[..., HttpResponseBase]]:
    """
    :param permissions: The permissions needed to access the endpoint.
    :param query: The serializer used for query parameters.
    :param parameters: The OpenAPI parameters for the endpoint.
    :param body: The serializer used for the request body.
    :param response: The OpenAPI schema for the response.
    :param responses: The OpenAPI schemas for various response codes.
    :param summary: A brief summary of the endpoint.
    :param description: A detailed description of the endpoint.
    :param tags: The tags associated with the endpoint.
    :param transaction: Whether to use a transaction for the endpoint.
    :param sqllogging: Whether to log SQL queries for the endpoint.
    :param deprecated: Whether to mark the endpoint as deprecated.
    :param kwargs: Additional keyword arguments to pass to the `extend_schema` decorator.
    """

    def decorator(func, cls=None):
        args = ArgCollection(
            func=func,
            cls=cls,
            permissions=permissions,
            query=query,
            body=body,
            response=response,
            responses=responses,
            summary=summary,
            description=description,
            summary_from_doc=summary_from_doc,
            tags=tags,
            transaction=transaction,
            sqllogging=sqllogging,
            deprecated=deprecated,
        )
        is_first_call = not hasattr(func, "argcollection")

        if not is_first_call:
            args = getattr(func, "argcollection").override(args)

        _responses = _get_responses(args)
        _summary, _description = _get_summary_and_description(args)

        if is_first_call:
            func = _response_decorator(func, args)
            if query is not None or is_not_empty_none(body):
                func = _request_decorator(func, args)
            if with_override(api_settings.TRANSACTION, transaction):
                func = _transaction.atomic(func)
            if with_override(api_settings.SQL_LOGGING, sqllogging):
                func = _sql_logging_decorator(func, args)
            if permissions:
                func = _permission_decorator(func, args)
            func = _excpetion_catcher(func, args)
            setattr(func, "argcollection", args)
        return extend_schema(
            parameters=parameters or ([args.query] if args.query else None),
            request=(None if is_action_view(args.func) else empty) if args.body is empty else args.body,
            responses=_responses,
            summary=_summary,
            description=_description,
            tags=tags,
            **kwargs,
        )(func)

    return decorator


def _get_responses(e: ArgCollection):
    response = e.response
    if response is not empty and inspect.isclass(response):
        response = e.response()
    responses = {} if e.responses is empty else e.responses
    if response is not empty:
        if isinstance(response, StatusResponse):
            responses.setdefault(response.status_code, response)
        else:
            responses.setdefault(status.HTTP_200_OK, response)
    if api_settings.ACTION_DEFAULTS_EMPTY and not any_success(responses) and is_action_view(e.func):
        responses = {status.HTTP_204_NO_CONTENT: None}
    if responses:
        responses = dict(sorted(responses.items(), key=lambda x: x[0]))
    else:
        responses = empty
    return responses


def _get_summary_and_description(e: ArgCollection):
    summary = e.summary
    description = e.description

    action_description = getattr(e.func, "kwargs", {}).get("description")
    if with_override(api_settings.SUMMARY_FROM_DOC, e.summary_from_doc):
        doc = action_description or e.func.__doc__
        if doc is not None and (summary is None or description is None):
            first_line, *lines = doc.strip().splitlines()
            if summary is None:
                summary = e.summary = first_line
            if description is None:
                if sys.version_info >= (3, 13):
                    if lines:
                        indent_length = min((len(i) - len(i.lstrip()) for i in lines))
                        lines = [i[indent_length:] for i in lines]
                description = e.description = "\n".join(lines).strip()
            description = description or true_empty_str
    else:
        description = action_description or getattr(e.cls, "__doc__")

    if api_settings.SHOW_PERMISSIONS:
        permissions: list = list(drf_api_settings.DEFAULT_PERMISSION_CLASSES)
        permissions.extend(getattr(e.cls, "permission_classes", []))
        permissions.extend(e.permissions or [])
        permissions = [
            j for j in (i.__name__ if not isinstance(i, str) else i for i in permissions) if j != AllowAny.__name__
        ]
        if permissions:
            permissions_doc = f"**Permissions:** `{'` `'.join(permissions)}`"
            description = f"{permissions_doc}\n\n{description or ''}"
    return summary, description


def _response_decorator(func: Callable, e: ArgCollection):
    @functools.wraps(func)
    def wrapper(event: ProcessEvent) -> HttpResponseBase:
        response = func(*event.args, **event.kwargs)
        if response is None:
            response = Response(status=status.HTTP_204_NO_CONTENT)
        elif isinstance(response, HttpResponseBase):
            response = response
        else:
            response = Response(response)
        return response

    return wrapper


def _request_decorator(func: Callable, e: ArgCollection):
    f1 = None
    f2 = None

    @functools.wraps(func)
    def wrapper(event: ProcessEvent):
        nonlocal f1, f2

        if f1 := (e.query is not None if f1 is None else f1):
            if isinstance(e.query, serializers.BaseSerializer):
                serializer = copy(e.query)
                serializer.instance = event.get_object()
                serializer.initial_data = event.query_data
            else:
                serializer = e.query(instance=event.get_object(), data=event.query_data)
        elif f2 := (is_not_empty_none(e.body) if f2 is None else f2):
            if isinstance(e.body, serializers.BaseSerializer):
                serializer = copy(e.body)
                serializer.instance = event.get_object()
                serializer.initial_data = event.body_data
            else:
                serializer = e.body(instance=event.get_object(), data=event.body_data)
        else:
            raise ValueError("query or body is required")

        serializer.is_valid(raise_exception=True)
        serializer.context["request"] = event.request

        event.request.serializer = serializer
        event.request.validated_data = serializer.validated_data
        return func(event)

    return wrapper


def _sql_logging_decorator(func: Callable, e: ArgCollection):
    @functools.wraps(func)
    def wrapper(event: ProcessEvent):
        import sqlparse
        from rich import print as rprint
        from rich.padding import Padding

        response = func(event)
        cache = []
        for query in connection.queries:
            sql = sqlparse.format(query["sql"], reindent=api_settings.SQL_LOGGING_REINDENT).strip()
            cache.append(f"[SQL] Time: {query['time']}")
            cache.append(Padding(sql, (0, 0, 0, 2)))
        rprint(*cache)
        return response

    return wrapper


def _permission_decorator(func: Callable, e: ArgCollection):
    __permissions = None

    @functools.wraps(func)
    def wrapper(event: ProcessEvent):
        nonlocal __permissions

        for permission in (__permissions := __permissions or [permission() for permission in (e.permissions or [])]):
            if permission.has_permission(event.request, event.view):  # type: ignore
                return func(event)
        raise HttpError(_("You do not have permission to perform this action."), status=status.HTTP_403_FORBIDDEN)

    return wrapper


def _excpetion_catcher(func: Callable, e: ArgCollection):
    def handle_exception(event: ProcessEvent):
        try:
            response = func(event)
        except Http404 as exc:
            raise exc
        except HttpError as exc:
            return Response(exc.content, status=exc.status)
        except ValidationError as exc:
            return Response({"errors": exc.detail}, status=exc.status_code)
        except NotFound:
            return Response({"detail": _("Not found.")}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            traceback.print_exc()
            if is_accept_json(event.request):
                return Response({"detail": _("Server error.")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            raise exc
        return response

    @functools.wraps(func)
    def default_wrapper(*args, **kwds):
        if hasattr(args[0], "request"):
            request, view = args[1], args[0]
        else:
            request, view = args[0], None
        event = ProcessEvent(request=request, view=view, args=args, kwargs=kwds)
        return handle_exception(event)

    return default_wrapper
