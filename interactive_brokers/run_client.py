from client import IBClient

def main():
    # init client
    ib_client = IBClient()

    # re-authenticate if needed
    if ib_client.is_authenticated()['authenticated'] is False:
        print('No longer authenticated. Gateway timeouts if idle for a few minutes. '
            'Run ib_client.tickle() more often. Re-authenticating...\n')
        ib_client.reauthenticate()

    # check user sso validated
    print('Validated user:', ib_client.validate()['USER_NAME'], '\n')

    # todo: figure out why get_account_balance breaks. STATUS CODE: 500
    # balance = ib_client.get_account_balance()
    # print(balance)

    # current live orders
    live_orders = ib_client.get_live_orders()['orders']
    if len(live_orders)==0:
        print('No live orders\n')
    else:
        print('Current live orders:')
        df_live_orders = pd.DataFrame.from_dict(live_orders)
        print(df_live_orders)

if __name__ == "__main__":
    main()