import click
from tabulate import tabulate

cli    = click
option = click.option

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def command(**kargs):
    kargs['context_settings'] = CONTEXT_SETTINGS
    return cli.command(**kargs)

def trim(s, len_=30, end=' [...]'):
    assert len(end)<=len_
    out = str(s)
    if len(out)>len_:
        out = out[:(len_-len(end))] + end
    return out 



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
