"""Abstract Base static Class for every service."""
from abc import ABC, abstractmethod
import requests

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

    has_external_request = True
    """
    True if the service needs to reach out to an external http endpoint, False
    otherwise.
    """
    is_authenticated = False
    """
    True if the external request needs to be authenticated (i.e. with an
    Authorization header), False otherwise.

    .. note::
        This is taken into account only if `has_external_request` is set to True
    """
    access_token = None
    """
    Contains the access token for the OAuth authentication if present, None
    otherwise.

    .. note::
        This is taken into account only if `is_authenticated` is set to True
    """

    @classmethod
    def preprocess(cls, url, json):
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
    def get(cls, url):
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
    def postprocess(cls, response):
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
        pass

    @classmethod
    def authenticate(cls):
        """
        Authenticate the service on the service provider API.
        
        Update the `access_code` variable with the newly refreshed valid access
        token.
        """
        pass

    @classmethod
    def get_media(cls, url, json):
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
        processed_url = cls.preprocess(url, json)

        response = cls.get(processed_url)
        if cls.has_external_request:
            if cls.is_authenticated and response.status_code == 401:
                cls.authenticate()
                response = cls.get(processed_url)
            if response.status_code >= 300:
                raise MediaRetrievalError(
                    {
                        "service": cls.__name__,
                        "reddit_media_url": url,
                        "processed_media_url": processed_url,
                    }
                )
        return cls.postprocess(response)
