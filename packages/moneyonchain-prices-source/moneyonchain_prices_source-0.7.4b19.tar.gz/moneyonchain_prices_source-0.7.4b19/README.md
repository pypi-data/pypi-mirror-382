# **MoC prices source**

This is the python package used in [**Money on Chain**](https://moneyonchain.com/) projects where it is required to get the coinpair values directly from the sources.
This package includes a CLI tool that allows you to query the coinpair values in the same way that [**Money on Chain**](https://moneyonchain.com/) projects do.



## How to use it in your project

A simple example, do some imports first

```python
user@host:~$ python3
Python 3.8.5 (default, Jul 28 2020, 12:59:40) 
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from moc_prices_source import get_price, BTC_USD
>>>
```

Get de `BTC/USD` coin pair

```python
>>> get_price(BTC_USD)
Decimal('29395.82')
>>> 
```

And that's it!

More [usage examples](docs/examples.md) can be seen [here](docs/examples.md)



## How the included CLI tool looks like

Here you can see how the output of the `moc_prices_source_check` command looks like

```shell
user@host:~$ moc_prices_source_check "BTC/USD"

From     To      V.    Exchnage    Response        Weight    %  Time
-------  ------  ----  ----------  ------------  --------  ---  ------
Bitcoin  Dollar        Bitfinex    $  67.10800K      0.18   18  1.64s
Bitcoin  Dollar        Bitstamp    $  66.99300K      0.22   22  1.82s
Bitcoin  Dollar        Coinbase    $  66.98946K      0.25   25  1.42s
Bitcoin  Dollar        Gemini      $  67.01356K      0.17   17  2.05s
Bitcoin  Dollar        Kraken      $  67.00500K      0.18   18  1.64s

    Coin pair      Mediam     Mean    Weighted median  Sources    Ok
--  -----------  --------  -------  -----------------  ---------  ----
↓   BTC/USD         67005  67021.8              67005  5 of 5     ✓

Response time 2.06s

user@host:~$ 
```

This command has many options. you can run `moc_prices_source_check --help` to get help on how to run them.
More information about this CLI tool can be seen [here](docs/cli.md).



## References

* [Source code in Github](https://github.com/money-on-chain/moc_prices_source)
* [Package from Python package index (PyPI)](https://pypi.org/project/moneyonchain-prices-source)



## Requirements

* Python 3.6+ support



## Installation

### From the Python package index (PyPI) 

Run:

```shell
$ pip3 install moneyonchain-prices-source 
```

And then run:

```shell
$ moc_prices_source_check --version
```

To verify that it has been installed correctly

### From source

Download from [Github](https://github.com/money-on-chain/moc_prices_source)

Standing inside the folder, run:

```shell
$ pip3 install -r requirements.txt 
```

For install the dependencies and then run:

```shell
$ pip3 install .
```

Finally run:

```shell
$ moc_prices_source_check --version
```

To verify that it has been installed correctly



## Supported coinpairs and symbols

[Here](docs/supported_coinpairs.md) you can find an [summary of supported coinpairs and symbols](docs/supported_coinpairs.md)

