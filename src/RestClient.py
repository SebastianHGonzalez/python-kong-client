from requests import session


class RestClient:

    def __init__(self, url, session=session()):
        self._session = session

        # TODO: validate url
        self.url = url

    @property
    def session(self):
        # TODO: research sessions inner workings
        return self._session
