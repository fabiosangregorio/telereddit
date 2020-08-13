"""Abstract Base static Class for every service."""
from abc import ABC, abstractmethod
import requests
from requests import Response
import icontract

from typing import Optional, Any, Union

from telereddit.models.media import Media
from telereddit.exceptions import MediaRetrievalError


class Service(ABC):
    """
    Abstract Base static Class for every service class.

    Summary
    -------
    This class contains all the common logic to the media retrieval process in
    all child services.

    This consists of the `get_media()` method, which executes the following
    steps (in order):

    * URL preprocessing
    * Media information get
    * re-authentication if necessary
    * URL postprocessing and Media object creation

    All the implementation logic is delegated to the child classes, since every
    service provider has custom logic, although the base class offers some basic
    implementation, which can be easily overwritten.

    Notes
    -----
    Authenticated services need to present an `__init__` method in which the
    specific service authentication method is called, in order to authenticate
    for the first time on the Service creation.

    """

    has_external_request: bool = True
    """
    True if the service needs to reach out to an external http endpoint, False
    otherwise.
    """
    is_authenticated: bool = False
    """
    True if the external request needs to be authenticated (i.e. with an
    Authorization header), False otherwise.

    .. note::
        This is taken into account only if `has_external_request` is set to True
    """
    access_token: Optional[str] = None
    """
    Contains the access token for the OAuth authentication if present, None
    otherwise.

    .. note::
        This is taken into account only if `is_authenticated` is set to True
    """

    @classmethod
    @icontract.require(
        lambda cls, url, json: url is not None, "url must not be None"
    )
    @icontract.ensure(lambda result: result is not None)
    def preprocess(cls, url: str, json: Any) -> str:
        """
        Preprocess the media URL coming from Reddit json.

        Returned url should match the service provider API URL structure, from
        which to get the media information.

        Parameters
        ----------
        url : str
            Reddit media URL to preprocess.
        json : json
            Json from the Reddit API which contains the post data. Used to get
            fallback media urls for specific services.

        Returns
        -------
        str
            Preprocessed url related to the service provider API.

        """
        return url

    @classmethod
    @icontract.require(lambda cls, url: url is not None, "url must not be None")
    @icontract.ensure(lambda result: result is not None)
    def get(cls, url: str) -> Union[Response, str]:
        """
        Get the media information.

        This is usually through an http request to the service provider API.

        .. note::
            In case the request needs to be authenticated, this method assumes a
            valid access token is stored in `access_token`.

        Parameters
        ----------
        url : str
            URL related to the specific service provider API, on which an http
            request can be fired to get the media information.

        Returns
        -------
        `requests.models.Response`
            Response from the service provider API.

        """
        return requests.get(url, stream=True)

    @classmethod
    @abstractmethod
    @icontract.require(
        lambda cls, response: response is not None, "response must not be None"
    )
    @icontract.ensure(lambda result: result is not None)
    def postprocess(cls, response: Union[Response, str]) -> Media:
        """
        From the service provider API response create the media object.

        .. warning::
            This is the only abstract method of the class. Thus it needs to be
            implemented in each child class. This is due to the intrinsic
            inexistence of a common pattern on which to create the media object.

        Parameters
        ----------
        response : `requests.models.Response`
            Response from the service provider API.

        Returns
        -------
        `telereddit.models.media.Media`
            Media object related to the media retrieval process.

        """
        raise NotImplementedError()

    @classmethod
    def authenticate(cls) -> None:
        """
        Authenticate the service on the service provider API.

        Update the `access_code` variable with the newly refreshed valid access
        token.
        """
        pass

    @classmethod
    @icontract.require(
        lambda cls, url, json: url is not None, "url must not be None"
    )
    @icontract.ensure(lambda result: result is not None)
    def get_media(cls, url: str, json: Any) -> Media:
        """
        Entrypoint of the class.

        Takes care of the common logic of media information retrieval, which
        consists in executing the following steps (in order):

        * `Service.preprocess()`
        * `Service.get()`
        * `Sercice.authenticate()` if the access token is not valid.

            (and then again `Service.get()`)

        * `Service.preprocess()`

        .. caution::
            This method **should not** be overwritten by child classes.

        Parameters
        ----------
        url : str
            Media URL from the Reddit API json.
        json : json
            Json from the Reddit API which contains the post data. Used to get
            fallback media urls for specific services.

        Returns
        -------
        `telereddit.models.media.Media`
            The media object accessible from the application.

        """
        processed_url: str = cls.preprocess(url, json)

        response: Union[Response, str] = cls.get(processed_url)
        if cls.has_external_request:
            if cls.is_authenticated and response.status_code == 401:  # type: ignore
                cls.authenticate()
                response = cls.get(processed_url)
            if response.status_code >= 300:  # type: ignore
                raise MediaRetrievalError(
                    {
                        "service": cls.__name__,
                        "reddit_media_url": url,
                        "processed_media_url": processed_url,
                    }
                )
        return cls.postprocess(response)
