import requests
import six
from config import DevelopmentConfig, ProductionConfig
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pandas as pd
from datetime import datetime


API_ROOT_URL = "https://api.yelp.com/v3"

BUSINESS_PATH = "/v3/businesses/{business_id}"
PHONE_SEARCH_PATH = "/v3/businesses/search/phone"
SEARCH_PATH = "/v3/businesses/search"


class YelpClient(object):
    def __init__(self, api_key):
        self._session = requests.Session()
        self._session.headers.update(self._get_auth_header(api_key))

        self._transport = RequestsHTTPTransport(url='https://api.yelp.com/v3/graphql', headers=self._get_auth_header(api_key), use_json=True)
        self.graphql_client = Client(transport=self._transport, fetch_schema_from_transport=True,)


    def _make_request(self, path, url_params=None):
        url_params = url_params if url_params is not None else {}

        url = "{}{}".format(
            API_ROOT_URL, six.moves.urllib.parse.quote(path.encode("utf-8"))
        )

        response = self._session.get(url, params=url_params)

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': response.status_code}

    def _get_auth_header(self, api_key):
        return {"Authorization": "Bearer {api_key}".format(api_key=api_key)}

    def graphQL_search(self, term, location, offset=0):

        if not offset:
            qry = '{search (location: "' + location + '", term: "' + term + '", sort_by: "rating", open_now: true, limit: 30) {'
        else:
            qry = '{search (location: "' + location + '", term: "' + term + '", offset:' \
                    + str(offset) + ', sort_by: "rating" open_now: true, limit: 30) {'

        qry += ''' total business {id name rating review_count coordinates {latitude, longitude} location {address1 address2 address3 city state country}}}}'''

        res = self.graphql_client.execute(gql(qry))

        return res

    def get_spots(self, term, location):
        offset = 0

        res = self.graphQL_search(term, location, offset=offset)
        total, spots = self.process_query(res)

        if len(spots) >= total:
            return spots
        final = spots

        while len(final) <= total and len(spots) > 0:
            offset += 30
            try:
                res = self.graphQL_search(term, location, offset)
                total, spots = self.process_query(res)
                print(total, spots)
                print(offset)
                final += spots
            except Exception as e:
                print(e)
                break

        df = pd.json_normalize(final)
        cols = []
        for c in df.columns:
            if '.' in c:
                cols.append(c.split('.')[1])
            else:
                cols.append(c)
        df.columns = cols

        df.loc[:, 'tdate'] = datetime.today()
        return df


    def process_query(self, res):
        data = res['search']
        total = data['total']
        business = data['business']
        return total, business


if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.engine.url import URL

    clt = YelpClient(DevelopmentConfig.yelp_api_key)

    url = "/businesses/yelp-san-francisco"

    res = clt.get_spots('restaurant', 'flushing')

    engine = create_engine(URL(**ProductionConfig().DATABASE))

    res.to_sql('yelp_restaurants', con=engine, schema='dbo', if_exists='append', index=False)



