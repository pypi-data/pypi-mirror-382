import json
from datetime import (
    datetime,
    timedelta,
)
from logging import getLogger
from typing import (
    Dict,
    List,
    Tuple,
    Union,
)
from urllib.parse import urljoin

import requests

__version__ = '5.0.0'

from requests import ReadTimeout


class EventType:
    """
    The EventType object identifies the type of an event. EventType is included both when publishing events
    and in events received.

    :param namespace: Roughly corresponds to the source of the events.
    :param event_name: A distinct name within the namespace that tells what the event is for.
    """

    def __init__(self, namespace: str, event_name: str):
        self.namespace = namespace
        self.event_name = event_name

    def __eq__(self, other):
        return isinstance(other, EventType) and self.namespace == other.namespace and self.event_name == other.event_name

    def __str__(self):
        return ":".join((self.namespace, self.event_name))

    def __repr__(self):
        return f'<EventType {self.namespace}:{self.event_name}>'

    @staticmethod
    def parse(s: str) -> 'EventType':
        """Create EventType object from event type string in event."""
        namespace, separator, event_name = s.partition(':')
        assert separator
        return EventType(namespace=namespace, event_name=event_name)


class PublishEvent:
    """
    The PublishEvent object identifies an event to be published.

    :param event_id: ID of the event. This is set by the publisher and will be part of the event received by
                     the subscriber.
    :param event_type: Type of event.
    :param role_grants: List of grants required to access the event. A subscriber can access the event if
                        it has any of the grants in the list.
    :param payload: JSON serializable object. The payload is forwarded to subscribers as is.
    """

    def __init__(self, event_id: str, event_type: EventType, role_grants: List[Dict[str, str]], payload: object):
        self.event_id = event_id
        self.event_type = event_type
        self.role_grants = role_grants
        self.payload = payload

    def __eq__(self, other):
        return (
            isinstance(other, PublishEvent)
            and self.event_id == other.event_id
            and self.event_type == other.event_type
            and self.role_grants == other.role_grants
            and self.payload == other.payload
        )

    def __repr__(self):
        return f'<PublishEvent event_id={self.event_id} event_type={self.event_type} role_grants={self.role_grants}>'


class Event:
    """
    The Event object identifies an event received.

    :param event_id: ID of the event. This is set by the publisher.
    :param event_type: Type of event.
    :param ack_ref: Acknowledgement reference to be used in ACK requests. Including this in an ACK means that the
                    subscriber confirms that it has processed all events up to, and including, the event that
                    the ack_ref was taken from.
    :param payload: JSON serializable object. The payload is forwarded from the publisher as is.
    """

    def __init__(self, event_id: str, event_type: EventType, ack_ref: str, payload: object):
        self.event_id = event_id
        self.event_type = event_type
        self.ack_ref = ack_ref
        self.payload = payload

    def __eq__(self, other):
        return (
            isinstance(other, Event)
            and self.event_id == other.event_id
            and self.event_type == other.event_type
            and self.ack_ref == other.ack_ref
            and self.payload == other.payload
        )

    def __repr__(self):
        return f'<Event event_id={self.event_id} event_type={self.event_type} ack_ref={self.ack_ref}>'


class Subscription:
    """
    The Subscription object contains information about the state of a subscription.

    :param event_types: The event types that the subscription is for.
    :param user_id: The user id of the subscriber.
    :param offset: The offset in the event stream that the subscription is currently at.
    """

    def __init__(self, event_types: List[EventType], user_id: str, offset: str):
        self.event_types = event_types
        self.user_id = user_id
        self.offset = offset

    def __eq__(self, other):
        return (
            isinstance(other, Subscription)
            and self.event_types == other.event_types
            and self.user_id == other.user_id
            and self.offset == other.offset
        )

    def __repr__(self):
        return f'<Subscription user_id={self.user_id} event_types={self.event_types} offset={self.offset}>'


class PublishTopic:
    """
    The PublishTopic object holds information about a specific event type to be published.

    :param event_name: Name of event to be published.
    :param role_required: The role required to access this event.
    :param scopes_required: List of scopes required to access this events. A subscriber can access the event only if
                            it has all of the listed scopes.
    """

    def __init__(self, event_name: str, role_required: str, scopes_required: List[str]):
        self.event_name = event_name
        self.role_required = role_required
        self.scopes_required = scopes_required

    def __eq__(self, other):
        return (
            isinstance(other, PublishTopic)
            and self.event_name == other.event_name
            and self.role_required == other.role_required
            and self.scopes_required == other.scopes_required
        )

    def __repr__(self):
        return f'<PublishTopic event_name={self.event_name} roles_required={self.role_required} scopes_required={self.scopes_required}>'


class Topic:
    """
    The topic object holds information about a particular topic that a subscriber can subscribe to.

    :param event_type: The event type of the topic.
    """

    def __init__(self, event_type: EventType):
        self.event_type = event_type

    def __eq__(self, other):
        return isinstance(other, Topic) and self.event_type == other.event_type

    def __str__(self):
        return ":".join((self.event_type.namespace, self.event_type.event_name))

    def __repr__(self):
        return f'<Topic {self.event_type.namespace}:{self.event_type.event_name}>'


class TriUnauthorized(Exception):
    """ Raised when a user is unauthorized to access the API. Eg. a 401 is returned."""
    pass


class TriAuthSessionException(Exception):
    """Raised when authentication fails for some reason."""
    pass


class TriException(Exception):
    """Raised upon unexpected responses."""

    def __init__(self, response):
        self.response = response
        super().__init__()

    def __str__(self):
        return f"<{self.__class__.__name__}: Code: {self.response.status_code} Result: {self.response.text} >"


class TriventTimeout(ReadTimeout):
    base_url: str

    def __init__(self, request, response, base_url: str):
        self.base_url = base_url
        super().__init__(request=request, response=response)


class AuthenticatedSession(requests.Session):
    """
    Create a session object that can be used to interact with TriOptima endpoints that authentication.

    :param client_id: Oauth Client ID of the user logging in.
    :param client_secret: Oauth Client Secret of the user logging in.
    :param username: Username of the user logging in. If using username and password to authenticate.
    :param password: Password of the user logging in. If using username and password to authenticate.
    :param refresh_token: Refresh token for the user logging in. If using refresh token to authenticate.
    :param scope: Scopes to request as a space separated list.
    :param base_url: TriOptima URL, eg. https://secure.trioptima.com.
    :param auth_url: URL to authenticate against. If not set this will be the same as base_url.
    :param proxies: Requests style dict with any HTTP proxies that may be needed.
    :param timeout: Requests style timeout tuple for connect and read timeout.
    """

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            username: str = None,
            password: str = None,
            refresh_token: str = None,
            scope: str = None,
            base_url: str = '',
            auth_url: str = None,
            token_url: str = None,
            access_token: str = None,
            proxies: Dict[str, str] = None,
            timeout: Union[float, Tuple[float, float]] = None,
    ):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.refresh_token = refresh_token
        self.base_url = base_url
        self.auth_url = auth_url or base_url
        self.token_url = token_url or urljoin(self.auth_url, '/auth/api/v1/token')
        self.scope = scope
        self.access_token = access_token
        self.token_expiry = None
        self.proxies = proxies
        self.timeout = timeout

        if (username or password) and bool(refresh_token):
            raise Exception('Authentication requires username and password OR refresh token.')

    def _request(self, method, url, *args, **kwargs):
        if self.proxies:
            kwargs.setdefault('proxies', self.proxies)

        kwargs.setdefault('timeout', self.timeout)
        return super().request(method, url, *args, **kwargs)

    def _authenticate(self):
        token_is_expired = self.token_expiry is not None and datetime.now() > self.token_expiry
        authentication_needed = token_is_expired or self.access_token is None

        if authentication_needed:
            params = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            if self.scope:
                params['scope'] = self.scope

            if self.refresh_token:
                params['grant_type'] = 'refresh_token'
                params['refresh_token'] = self.refresh_token

            if self.username and self.password:
                params['grant_type'] = 'password'
                params['username'] = self.username
                params['password'] = self.password

            resp = self._request('POST', self.token_url, data=params)

            if not resp.status_code == 200:
                raise TriAuthSessionException(f'Authentication failed: {resp.text}')
            try:
                data = resp.json()
                access_token = data['access_token']
                expires_in = data.get('expires_in', None)
            except (ValueError, KeyError) as e:
                raise TriAuthSessionException(f'Unable to parse token response. Exception: {e} Response: {resp.text}')

            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60) if expires_in else None
            self.access_token = access_token
            return data

    def request(self, method, url, *args, **kwargs):
        """
        Make an authorized request. This method can be called directly but is also used by convenience methods
        on the request.Session object such as `get`, `post`, `put`, etc.

        :param method: The HTTP method to use.
        :param url: The URL to make the request against.
        :param args: Any additional args, passed on to requests.
        :param kwargs: Any additional kwargs, passed on to requests.

        :return: A `requests.Response` object.
        """
        return self._try_request(method, url, *args, is_retry=False, **kwargs)

    def _try_request(self, method, url, is_retry, *args, **kwargs,):
        self._authenticate()
        if self.access_token:
            self.headers['Authorization'] = 'Bearer ' + self.access_token
        url = urljoin(self.base_url, url)
        resp = self._request(method, url, *args, **kwargs)

        if resp.status_code == 401 and not is_retry:
            # There are different circumstances under which the access token may be invalidated
            # before the timeout has expired. Make one attempt to re-authenticate.
            self.access_token = None
            return self._try_request(method, url, *args, is_retry=True, **kwargs)

        return resp


class EventSession(AuthenticatedSession):
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        username: str = None,
        password: str = None,
        refresh_token: str = None,
        scope: str = None,
        debug: bool = False,
        auth_url: str = None,
        logger_name: str = "tri.event",
        proxies: Dict[str, str] = None,
        timeout: Union[float, Tuple[float, float]] = (5.0, 5.0),
    ):
        """
        Create a session object that can be used to interact with /events and other API endpoints.

        :param base_url: TriOptima URL, eg. https://secure.trioptima.com.
        :param client_id: Oauth Client ID of the user logging in.
        :param client_secret: Oauth Client Secret of the user logging in.
        :param username: Username of the user logging in. If using username and password to authenticate.
        :param password: Password of the user logging in. If using username and password to authenticate.
        :param refresh_token: Refresh token for the user logging in. If using refresh token to authenticate.
        :param scope: Scopes to request as a space separated list.
        :param debug: If set to true some additional information will be printed for every request.
        :param auth_url: URL to authenticate against. If not set this will be the same as base_url.
        :param logger_name: Name to use when logging standard error/warning/info/debug messages.
        :param proxies: Requests style dict with any HTTP proxies that may be needed.
        :param timeout: Requests style timeout tuple for connect and read timeout.


        Example, subscriber:

        >>> from tri_api import EventSession, EventType
        >>> from time import sleep
        >>> SCOPE = "b3092535-28c2-11e7-a0ad-012345678900:a_scope"
        >>> session = EventSession(
        ...     client_id="f817cb52-c003-11e9-acd3-123456789000",
        ...     client_secret="367a89a4ae6c5ee84f44123456789000",
        ...     username="my_subscriber_user",
        ...     password="XyZ0123!",
        ...     scope=f"profile {SCOPE}",
        ...     base_url="https://secure.trioptima.com/")
        >>> session.subscribe([EventType("interesting_namespace", "interesting_event_name")])
        >>> sleep(5)
        >>> events = session.poll(limit=10)
        >>> if events:
        ...     print(events)
        ...     session.ack(events[-1].ack_ref)
        <Event event_id=123 event_type=<EventType interesting_namespace:interesting_event_name> ack_ref=abcd>
        <Event event_id=456 event_type=<EventType interesting_namespace:interesting_event_name> ack_ref=efgh>


        Example, publisher:

        >>> from tri_api import EventSession, EventType, PublishTopic, PublishEvent
        >>> SCOPE = "e5077612-e1b9-11e8-9fed-02420a140605:publish_events"
        >>> session = EventSession(
        ...     client_id="f817cb52-c003-11e9-acd3-123456789000",
        ...     client_secret="367a89a4ae6c5ee84f44123456789000",
        ...     username="my_publisher_user",
        ...     password="XyZ0123!",
        ...     scope=f"profile {SCOPE}",
        ...     base_url="https://secure.trioptima.com/")
        >>> session.publish_intent("my_namespace", intents=[PublishTopic(event_name="my_event",
        ...                                                              role_required="my_role",
        ...                                                              scopes_required=['global'])])
        >>> session.publish(events=[PublishEvent(event_id="111",
        ...                                      event_type=EventType(namespace="my_namespace", event_name="my_event"),
        ...                                      role_grants=[{"property": "value"}],
        ...                                      payload={"data": "to send"})])

        """

        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            refresh_token=refresh_token,
            scope=scope,
            base_url=base_url,
            auth_url=auth_url,
            proxies=proxies,
            timeout=timeout,
        )

        self.debug = debug
        self.log = getLogger(logger_name)

    def request(self, method, url, expected_status_code=200, *args, **kwargs):
        """
        Make an authorized request. This method can be called directly but is also used by convenience methods
        on the request.Session object such as `get`, `post`, `put`, etc.

        :param method: The HTTP method to use.
        :param url: The URL to make the request against.
        :param expected_status_code: Status code expected in response, pass None to disable status code check.
        :param args: Any additional args, passed on to requests.
        :param kwargs: Any additional kwargs, passed on to requests.

        :return: A `requests.Response` object.

        :raise TriUnauthorized if 401 is returned.
        :raise TriException if status code differs from expected_status_code.
        """

        try:
            response = super().request(method, url, *args, **kwargs)
        except ReadTimeout as inner_error:
            raise TriventTimeout(
                request=inner_error.request,
                response=inner_error.response,
                base_url=self.base_url
            ) from inner_error

        if response.status_code == 401:
            raise TriUnauthorized
        if expected_status_code and response.status_code != expected_status_code:
            raise TriException(response=response)

        if self.debug and self.log:
            data = kwargs.get('json')
            if data:
                self.log.debug("Request: %s", json.dumps(data, indent=2))
            if response.text:
                if 'application/json' in response.headers['Content-Type']:
                    self.log.debug("Response: %s", json.dumps(json.loads(response.text), indent=2))
                else:
                    self.log.debug("Response: %s", response.text)

        return response

    def get_openapi(self) -> str:
        """
        Get OpenAPI spec for triVent in YAML format.

        :return: String with spec.
        """
        return self.get('/events/openapi.yaml', expected_status_code=200).text

    def publish_intent(self, namespace: str, intents: List[PublishTopic]) -> None:
        """
        Make a publish intent.

        :param namespace: The namespace for which the intent is made.
        :param intents: The different topics on which the client intents to publish.

        :raise TriException if publish intent fails.
        """
        topics = [
            {
                'event_name': intent.event_name,
                'role_required': f'{self.client_id}:{intent.role_required}',
                'scope_required': [
                    f'{self.client_id}:{scope}'
                    for scope in intent.scopes_required
                ],
            }
            for intent in intents
        ]

        self.put(
            f'/events/topics/{namespace}',
            json={'topics': topics},
            expected_status_code=201,
        )

    def get_topics(self) -> List[Topic]:
        """
        List all topics that the user has permission to access.

        :return List of topics.
        """
        response = self.get('/events/topics', expected_status_code=200)
        data = response.json()
        return [
            Topic(event_type=EventType.parse(topic['event_type']))
            for topic in data['topics']
        ]

    def subscribe(self, event_types: List[EventType]) -> None:
        """
        Subscribe to a list of event types/topics.

        :param event_types: Event types to subscribe to.

        :raise TriException if subscription fails.
        """
        response = self.put(
            '/events/subscriptions',
            json={
                'event_types': [
                    f'{e.namespace}:{e.event_name}'
                    for e in event_types
                ],
            },
            expected_status_code=None,
        )
        if response.status_code not in [200, 201]:
            raise TriException(response)

    def get_subscriptions(self, namespace) -> List[Subscription]:
        """
        List subscriptions for a particular namespace. The user must have permissions to publish on the
        namespace for this to succeed.

        :param namespace: Namespace to list subscriptions for.

        :return List of subscriptions.

        :raise TriException if request fails.
        """
        response = self.get(f'/events/subscriptions/{namespace}', expected_status_code=200)
        data = response.json()
        return [
            Subscription(
                event_types=[
                    EventType.parse(t)
                    for t in subscription['event_types']
                ],
                user_id=subscription['user_id'],
                offset=subscription['offset'],
            )
            for subscription in data['subscriptions']
        ]

    def publish(self, events: List[PublishEvent]) -> None:
        """
        Publish a list of events.

        :param events: Events to publish.

        :raise TriException if request fails.
        """
        pevents = [
            {
                "event_id": event.event_id,
                "event_type": str(event.event_type),
                "payload": event.payload,
                "role_grants": event.role_grants,
            }
            for event in events
        ]
        self.post(
            '/events',
            json={"events": pevents},
            expected_status_code=201,
        )

    def poll(self, limit=1) -> List[Event]:
        """
        Poll for events.

        :param limit: Maximum number of events to receive.

        :return: List of events.

        :raise TriException if request fails.
        """
        response = self.get('/events', params=dict(limit=limit), expected_status_code=200)
        data = response.json()
        return [
            Event(
                event_id=event['event_id'],
                event_type=EventType.parse(event['event_type']),
                ack_ref=event['ack_ref'],
                payload=event['payload'],
            )
            for event in data['events']
        ]

    def ack(self, ack_ref: str, allow_rewind: bool = False) -> None:
        """
        Acknowledge processing of all events up to, and including, event with supplied ack ref.

        :param ack_ref: Acknowledge reference received in event.
        :param allow_rewind: Allow acknowledging reference with an older offset than the current offset.

        :raise TriException if request fails.
        """
        self.put('/events/ack', json={'ack_ref': ack_ref, 'allow_rewind': allow_rewind}, expected_status_code=200)
