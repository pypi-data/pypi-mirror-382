from engine_base import BaseOnChain, RIF_BTC, get_env



class Engine(BaseOnChain):

    _name          = BaseOnChain._name_from_file(__file__)
    _description   = "Sovryn onchain"
    _coinpair      = RIF_BTC
    _uri           = get_env('RSK_NODE', 'https://public-node.rsk.co')
    _pool_sc_addr  = '0x65528e06371635a338ca804cd65958a11cb11009'
    _wrbtc_tk_addr = '0x542fda317318ebf1d3deaf76e0b632741a7e677d'
    _rif_tk_addr   = '0x2acc95758f8b5f583470ba265eb685a8f45fc9d5'

    def _get_price(self):

        pool_sc_addr = self.to_checksum_address(self._pool_sc_addr)
        wrbtc_tk_addr = self.to_checksum_address(self._wrbtc_tk_addr)
        rif_tk_addr = self.to_checksum_address(self._rif_tk_addr)

        str_error = None
        value = None

        try:            

            w3 = self.make_web3_obj_with_uri()

            rif_token = w3.eth.contract(address=rif_tk_addr, abi=self.erc20_simplified_abi)
            wrbtc_token = w3.eth.contract(address=wrbtc_tk_addr, abi=self.erc20_simplified_abi)

            rif_reserve = rif_token.functions.balanceOf(pool_sc_addr).call()
            btc_reserve = wrbtc_token.functions.balanceOf(pool_sc_addr).call()

            value = btc_reserve/rif_reserve

        except Exception as e:
            str_error = str(e)

        if value is None:
            self._error = str_error
        
        return value



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    if engine.error:
        print(f"{engine} Error: {engine.error}")
    else:
        print(engine)
