import os

import requests

from config import logger


DEVMAN_TOKEN=os.environ['DEVMAN_TOKEN']


class DevmanAPI:

    def __init__(self, url='https://dvmn.org/api/user_reviews/', timeout=None):
        self._url = url
        self._timeout = timeout
        self._params = {}

        self.response = self._make_request(url=self._url, params=self._params, timeout=self._timeout)


    def _make_request(self, url='', params=None, timeout=None):

        headers = {'Authorization': f'token {DEVMAN_TOKEN}'}

        while True:
            try:
                r = requests.get(url, headers=headers,
                                      params=params,
                                      timeout=timeout)
                r.raise_for_status()

            except requests.exceptions.ReadTimeout:
                logger.debug('Timeout', exc_info=True)
                continue
            except requests.exceptions.ConnectionError:
                logger.debug('Connection Error', exc_info=True)
                continue
            else:
                response = r.json()
                status = response.get('status')

                logger.debug(f'Got from server: {response}')

                if status == 'timeout':
                    params.update({'timestamp': response.get('timestamp_to_request')})
                    logger.debug(f"Server's timeout is running out. {response}")
                    continue
                elif status == 'found':
                    logger.debug(f'Server found submitted works - {response}')
                    return response
                else:
                    return None

    def __str__(self):
        return f'<DevmanAPI. Result: {self.response}>'


def main():
    polling_url = 'https://dvmn.org/api/long_polling/'
    devman = DevmanAPI(url=polling_url, timeout=100)


if __name__ == '__main__':
    main()
