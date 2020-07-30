from order import Order
import requests
from typing import Dict
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(category=InsecureRequestWarning)

class IBClient(object):
    def __init__(self):
        # Account info
        self.acctId = open('account_info.txt', 'r').read()

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
            response = requests.post(url, headers = headers, json=params, verify = False)

        # SCENARIO 2: POST without a payload.
        elif req_type == 'POST' and params is None:
            response = requests.post(url, headers = headers, verify = False)

        # SCENARIO 3: GET without parameters.
        elif req_type == 'GET' and params is None:
            response = requests.get(url, headers = headers, verify = False)

         # SCENARIO 4: GET with parameters.
        elif req_type == 'GET' and params is not None:
            response = requests.get(url, headers = headers, params = params, verify = False)

         # SCENARIO 5: DELETE (does not accept parameters).
        elif req_type == 'DELETE':
            response = requests.delete(url, headers = headers, verify = False)

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

        content = self._make_request(endpoint = endpoint, req_type = req_type)
        
        return content

    def logout(self) -> Dict:
        """End current session.
        Logs the user out of the gateway session. Any further activity requires 
        re-authentication.
        """

        # define request components
        endpoint = 'logout'
        req_type = 'POST'

        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def get_accounts(self) -> Dict:
        """Get accounts.
        Returns a list of accounts the user has trading access to, their respective aliases
        and the currently selected account. Note this endpoint must be called before modifying
        an order or querying open orders.
        """

        # define request components
        endpoint = 'iserver/accounts'
        req_type = 'GET'

        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

    def get_account_balance(self) -> Dict:
        """Get account balance(s).
        Returns a summary of all account balances for the given accounts, if more than
        one account is passed, the result is consolidated.
        """

        # define request components
        endpoint = 'pa/summary'
        req_type = 'POST'
        payload = {
            'acctIds': [self.acctId]
        }

        # this is special, I don't want the JSON content right away.
        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)
        
        return content

    def get_outstanding_orders(self):
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

    def get_conid(self, symbol: str):
        """Get current live orders. Returns and array of results.
        Symbol or name to be searched.
        Payload definitions:
        1. symbol: If symbol is warrant, warrant conid can be found in 'sections' in resulting array.
        2. (optional) name: should be true if the search is to be performed by name. false by default.
        3. (optional) secType: If search is done by name, only the assets provided in this field will
        be returned. Currently, only STK is supported.
        """

        # define request components
        endpoint = 'iserver/secdef/search'
        req_type = 'POST'
        payload = {
            'symbol': symbol,
            'name': True,
        }

        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        return content

    def preview_order(self, order: Order) -> Dict:
        """Place a new order.
        This endpoint allows you to preview order without actually submitting the order and you can
        get commission information in the response.
        """

        # define request components
        endpoint = 'iserver/account/{}/order/whatif'.format(self.acctId)
        req_type = 'POST'
        payload = {
            "acctId": order.get_acctId(),
            "conid": order.get_conid(),
            "secType": order.get_secType(),
            "cOID": order.get_cOID(),
            "parentId": order.get_parentId(),
            "orderType": order.get_orderType(),
            "listingExchange": order.get_listingExchange(),
            "outsideRTH": order.get_outsideRTH(),
            "price": order.get_price(),
            "side": order.get_side(),
            "ticker": order.get_ticker(),
            "tif": order.get_tif(),
            "referrer": order.get_referrer(),
            "quantity": order.get_quantity(),
            "fxQty": order.get_fxQty(),
            "useAdaptive": order.get_useAdaptive(),
            "isCurrencyConversion": order.get_isCurrencyConversion()
        }

        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        return content

    def new_order(self, order: Order) -> Dict:
        """Place a new order.
        Please note here, sometimes this endpoint alone can't make sure you submit the order 
        successfully, you could receive some questions in the response, you have to to answer 
        them in order to submit the order successfully. You can use "/iserver/reply/{replyid}" 
        end-point to answer questions.
        """

        # define request components
        endpoint = 'iserver/account/{}/order'.format(self.acctId)
        req_type = 'POST'
        payload = {
            "acctId": order.get_acctId(),
            "conid": order.get_conid(),
            "secType": order.get_secType(),
            "cOID": order.get_cOID(),
            "parentId": order.get_parentId(),
            "orderType": order.get_orderType(),
            "listingExchange": order.get_listingExchange(),
            "outsideRTH": order.get_outsideRTH(),
            "price": order.get_price(),
            "side": order.get_side(),
            "ticker": order.get_ticker(),
            "tif": order.get_tif(),
            "referrer": order.get_referrer(),
            "quantity": order.get_quantity(),
            "fxQty": order.get_fxQty(),
            "useAdaptive": order.get_useAdaptive(),
            "isCurrencyConversion": order.get_isCurrencyConversion()
        }

        content = self._make_request(endpoint = endpoint, req_type = req_type, params = payload)

        return content

    def delete_order(self, orderId: str) -> Dict:
        """Place a new order.
        Deletes an open order. Must call get_accounts() prior to deleting an order.
        Use get_outstanding_orders() to review open orders.

        Path parameters: account id, orderId (not cOID/order_ref)
        """

        # call iserver/accounts endpoint
        self.get_accounts()

        # define request components
        endpoint = 'iserver/account/{}/order/{}'.format(self.acctId, orderId)
        req_type = 'DELETE'

        content = self._make_request(endpoint = endpoint, req_type = req_type)

        return content

