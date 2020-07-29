from typing import Dict
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(category=InsecureRequestWarning)

class IBClient(object):
    def __init__(self):
        # Account info
        self.account_id = 'DU2527585'

        # URL components
        self.ib_gateway_path = 'https://localhost:5000'
        self.api_version = 'v1'

    def _build_url(self, endpoint: str) -> str:
        """Builds a url for a request.
        Arguments:
        ----
        endpoint {str} -- The URL that needs conversion to a full endpoint URL.
        Returns:
        ----
        {str} -- A full URL path.
        """

        # build the URL
        full_url = self.ib_gateway_path + '/' + self.api_version + '/portal/' + endpoint
        return full_url

    def _make_request(self, endpoint: str, req_type: str, params: Dict = None) -> Dict:
        """Handles the request to the client.
        Handles all the requests made by the client and correctly organizes
        the information so it is sent correctly. Additionally it will also
        build the URL.
        Arguments:
        ----
        endpoint {str} -- The endpoint we wish to request.
        req_type {str} --  Defines the type of request to be made. Can be one of four
            possible values ['GET','POST','DELETE','PUT']
        params {dict} -- Any arguments that are to be sent along in the request. That
            could be parameters of a 'GET' request, or a data payload of a
            'POST' request.
        
        Returns:
        ----
        {Dict} -- A response dictionary.
        """

        # first build the url
        url = self._build_url(endpoint = endpoint)

        # make sure it's a JSON String
        headers = {'Content-Type':'application/json'}

        # Scenario 1: POST with a payload.
        if req_type == 'POST' and params is not None:

            # grab the response.
            response = requests.post(url, headers = headers, json=params, verify = False)

        # SCENARIO 2: POST without a payload.
        elif req_type == 'POST' and params is None:

            # grab the response.
            response = requests.post(url, headers = headers, verify = False)

        # SCENARIO 3: GET without parameters.
        elif req_type == 'GET' and params is None:

            # grab the response.
            response = requests.get(url, headers = headers, verify = False)

         # SCENARIO 3: GET with parameters.
        elif req_type == 'GET' and params is not None:

            # grab the response.
            response = requests.get(url, headers = headers, params = params, verify = False)

        # grab the status code
        status_code = response.status_code

        # grab the response headers.
        response_headers = response.headers

        # Check to see if it was successful
        if response.ok:

            if response_headers.get('Content-Type','null') == 'application/json;charset=utf-8':
                return response.json()
            else:
                return response.json()

        # if it was a bad request print it out.
        elif not response.ok and url != 'https://localhost:5000/v1/portal/iserver/account':

            print('')
            print('-'*80)
            print("BAD REQUEST - STATUS CODE: {}".format(status_code))
            print("RESPONSE URL: {}".format(response.url))
            print("RESPONSE HEADERS: {}".format(response.headers))
            print("RESPONSE TEXT: {}".format(response.text))
            print('-'*80)
            print('')

    def validate(self) -> Dict:
        """Validates the current session for the SSO user."""

        # define request components
        endpoint = 'sso/validate'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def tickle(self) -> Dict:
        """Keeps the session open.
        If the gateway has not received any requests for several minutes an open session will 
        automatically timeout. The tickle endpoint pings the server to prevent the 
        session from ending.
        """

        # define request components
        endpoint = 'tickle'
        req_type = 'POST'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def is_authenticated(self) -> Dict:
        """Checks if session is authenticated.
        Current Authentication status to the Brokerage system. Market Data and 
        Trading is not possible if not authenticated, e.g. authenticated 
        shows False.
        """

        # define request components
        endpoint = 'iserver/auth/status'
        req_type = 'POST'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def reauthenticate(self) -> Dict:
        """Reauthenticates an existing session.
        Provides a way to reauthenticate to the Brokerage system as long as there 
        is a valid SSO session, see /sso/validate.
        """

        # define request components
        endpoint = 'iserver/reauthenticate'
        req_type = 'POST'

        # this is special, I don't want the JSON content right away.
        content = self._make_request(endpoint = endpoint, req_type = req_type)
        
        return content

    def get_account_balance(self) -> Dict:
        """Get account balance.
        Returns a summary of all account balances for the given accounts, if more than
        one account is passed, the result is consolidated.
        """

        # define request components
        endpoint = 'pa/summary'
        req_type = 'POST'

        payload = {
            'acctIds': [self.account_id]
        }

        # this is special, I don't want the JSON content right away.
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)
        
        return content

    def get_live_orders(self):
        """Get current live orders.
            The endpoint is meant to be used in polling mode, e.g. requesting every 
            x seconds. The response will contain two objects, one is notification, the 
            other is orders. Orders is the list of orders (cancelled, filled, submitted) 
            with activity in the current day. Notifications contains information about 
            execute orders as they happen, see status field.
        """

        # define request components
        endpoint = 'iserver/account/orders'
        req_type = 'GET'
        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def place_order(self, account_id: str, order: dict) -> Dict:
        """Place a new order.
            Please note here, sometimes this endpoint alone can't make sure you submit the order 
            successfully, you could receive some questions in the response, you have to to answer 
            them in order to submit the order successfully. You can use "/iserver/reply/{replyid}" 
            end-point to answer questions.

            Payload definitions:

            acctId: acctId is optional. It should be one of the accounts returned by /iserver/accounts.
            If not passed, the first one in the list is selected.

            conid: conid is the identifier of the security you want to trade, you can find the conid with
            /iserver/secdef/search.

            secType: conid:type for example 265598:STK

            cOID: Customer Order ID. An arbitrary string that can be used to identify the order, e.g
            "my-fb-order". The value must be unique for a 24h span. Please do not set this value for child
            orders when placing a bracket order.

            parentId: When placing bracket orders, the child parentId must be equal to the cOId (customer
            order id) of the parent.

            orderType: orderType can be one of MKT (Market), LMT (Limit), STP (Stop) or STP_LIMIT (stop limit)

            listingExchange: listingExchange is optional. By default we use "SMART" routing. Possible values
            are available via this end point: /v1/portal/iserver/contract/{{conid}}/info, see valid_exchange

            outsideRTH: set to true if the order can be executed outside regular trading hours.

            print: optional if order is MKT, for LMT, this is the limit price. For STP this is the stop price.

            side: SELL or BUY

            ticker: ticker

            tif: GTC (Good Till Cancel) or DAY. DAY orders are automatically cancelled at the end of the Day

            referrer: for example QuickTrade

            quantity: usually integer, for some special cases can be float numbers

            fxQty: double number, this is the cash quantity field which can only be used for FX conversion order.

            useAdaptive: If true, the system will use the Adaptive Algo to submit the order
            https://www.interactivebrokers.com/en/index.php?f=19091

            isCurrencyConversion: set to true if the order is a FX conversion order
        """

        # payload = {
        #     "acctId": self.account_id,
        #     "conid": 0,
        #     "secType": "string",
        #     "cOID": "string",
        #     "parentId": "string",
        #     "orderType": "string",
        #     "listingExchange": "string",
        #     "outsideRTH": true,
        #     "price": 0,
        #     "side": "string",
        #     "ticker": "string",
        #     "tif": "string",
        #     "referrer": "string",
        #     "quantity": 0,
        #     "fxQty": 0,
        #     "useAdaptive": false,
        #     "isCurrencyConversion": false
        # }
        
        # # define request components
        # endpoint = 'iserver/account/{}/order'.format(self.account_id)
        # req_type = 'POST'
        # content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        # return content