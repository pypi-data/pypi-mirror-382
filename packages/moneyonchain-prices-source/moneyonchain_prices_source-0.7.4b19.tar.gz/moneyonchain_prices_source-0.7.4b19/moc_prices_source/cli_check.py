import json, sys
from os.path import dirname, abspath
from decimal import Decimal


bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.insert(0, dirname(base_dir))

from moc_prices_source.cli            import command, option, tabulate, trim, cli
from moc_prices_source.weighing       import weighing
from moc_prices_source                import version
from moc_prices_source                import get_price, ALL, get_coin_pairs
from moc_prices_source.engines        import all_engines
from moc_prices_source.computed_pairs import show_computed_pairs_fromula, computed_pairs

sys.path = bkpath

def summary(coinpairs, md=False):

    summary_data = {}

    for name, weigh in weighing.as_dict.items():

        engine = all_engines[name]
        coinpair = engine.coinpair
        description = engine.description
        uri = engine.uri

        if not coinpair in summary_data:
            summary_data[coinpair] = {'type': 'direct', 'sources': []}
        
        summary_data[coinpair]['sources'].append({
            'weigh': weigh, 'name': description, 'uri': uri
        })

    for computed_coinpair, computed_data in computed_pairs.items():
        if not computed_coinpair in summary_data:
            requirements = computed_data['requirements']
            if all([(c in summary_data) for c in requirements]):
                if not computed_coinpair in summary_data:
                    summary_data[computed_coinpair] = {
                        'type': 'computed',
                        'requirements': requirements,
                        'formula': computed_data['formula'],
                        'formula_desc': computed_data['formula_desc']
                    }


    coinpairs_and_requirements = coinpairs[:]
    for coinpair in coinpairs:
        c_data = summary_data.get(coinpair, None) 
        if c_data and c_data['type']=='computed':
            for r in c_data['requirements']:
                if not r in coinpairs_and_requirements:
                    coinpairs_and_requirements.append(r)


    for key in list(summary_data.keys()):
        if not key in coinpairs_and_requirements:
            del summary_data[key]

    def show_title(title, level=1):
        if md:
            prev = {1:"## ", 2:"### "}[level]
            print(prev + ' '.join(title.split()))
        else:
            prev = {1:"", 2:"  "}[level]
            sep = {1:"=", 2:"-"}[level]
            print(prev + ' '.join(title.split()))
            print(prev + ' '.join(map(lambda x: sep*len(x), title.split())))

    def show_p(p):
        if md:
            print(p)
        else:
            print(f"    {p}")

    def show_table(table, headers=[], tablefmt='psql'):
        if md:
            if tablefmt=='psql':
                tablefmt='github'
        s = tabulate(table, headers=headers, tablefmt=tablefmt, floatfmt=".2f")
        if md:
            if tablefmt=='plain':
                print('```')
            print(s)
            if tablefmt=='plain':
                print('```')
        else:
            if tablefmt=='plain':
                s = tabulate([[s]], tablefmt='psql')        
            for l in s.split('\n'):
                print(f"    {l}")



    title = "Symbols"
    coins = []
    for pair in summary_data.keys():
        for c in [pair.from_, pair.to_]:
            if not c in coins:
                coins.append(c)
    coins.sort()
    table = [[c.symbol, c.name, c.small_symbol] for c in coins]
    table.sort()
    headers=['Symbol', 'Name', 'Char']
    print()
    show_title(title)
    print()
    show_table(table, headers)
    print()


    title = "Coinpairs"
    str_source = {
        'direct': 'Weighted',
        'computed': 'Computed'
    }
    table = [[str(pair), pair.from_.symbol+'/'+pair.to_.symbol, pair.variant,
             str_source[data['type']]] for pair, data in summary_data.items()]
    table.sort()
    headers=['Name', 'Coinpair', 'Variant', 'Method']
    print()
    show_title(title)
    print()
    show_table(table, headers)
    print()
    table = [
        ['Weighted', 'Weighted median of values ​​obtained from multiple sources'],
        ['Computed', 'Compute made with previously obtained coinpairs']
    ]
    headers=['Method', 'Description']
    show_table(table, headers)
    print()
    table = [[str(pair), pair.description] for pair, data in summary_data.items()]
    table.sort()
    headers=['Name', 'Comment/Description']
    show_table(table, headers)
    print()    


    title="Formulas used in the computed coinpairs"
    table=[[str(pair), '=', data['formula_desc']] for pair, data in
           summary_data.items() if data['type']=='computed']
    table.sort()
    print()
    show_title(title)
    print()
    show_table(table, tablefmt='plain')
    print()


    title="Weights used for each obtained coinpairs from multiple sources"
    print()
    show_title(title)
    print()
    show_p("""If a price source is not available, this source is discarded
and the rest of the sources are used but with their weights recalculated
proportionally.""")
    show_p("""For example, you have 3 sources with 3 weights A:0.2, B:0.5, C:0.3
and if for some reason B would not be available, A:0.4, C:0.6 would
be used.""")
    print()
    show_p("""The weights used are fixed values.""")
    show_p("""These weightings are related to the historical volume handled by each
price source.""")
    show_p("""Every established period of time we review the historical volume of the
sources and if necessary we apply the changes to the parameterization.""")
    print()
    for pair, data in summary_data.items():
        if data['type']=='direct':
            title = f"For coinpair {pair.long_name}"
            sources = data['sources']
            table = [[d['name'], float(d['weigh']), d['uri']] for d in
                     sources if float(d['weigh'])>0]
            headers=['Source', 'Weight', 'URI']
            print()
            show_title(title, 2)
            print()
            if len(table)>1:
                show_table(table, headers)
            else:
                show_p(f"Only {table[0][0]} (URI: {table[0][2]})")
            print()


@command()
@option('-v', '--version', 'show_version', is_flag=True,
        help='Show version and exit.')
@option('-j', '--json', 'show_json', is_flag=True,
        help='Show data in JSON format and exit.')
@option('-w', '--weighing', 'show_weighing', is_flag=True,
        help='Show the default weighing and exit.')
@option('-c', '--computed', 'show_computed_pairs', is_flag=True,
        help='Show the computed pairs formula and exit.')
@option('-s', '--summary', 'show_summary', is_flag=True,
        help='Show the summary and exit.')
@option('-m', '--markdown', 'md_summary', is_flag=True,
        help='Set markdown for the summary format.')
@option('-n', '--not-ignore-zero-weighing', 'not_ignore_zero_weighing',
        is_flag=True, help='Not ignore sources with zero weighing.')
@cli.argument('coinpairs_filter', required=False)
def cli_check(
        show_version=False,
        show_json=False,
        show_weighing=False,
        show_computed_pairs=False,
        coinpairs_filter=None,
        show_summary=False,
        md_summary=False,
        not_ignore_zero_weighing=False
    ):
    """\b
Description:
    CLI-type tool that shows the data obtained by
    the `moc_price_source` library.   
    Useful for troubleshooting.
\n\b
COINPAIRS_FILTER:
    Is a display pairs filter that accepts wildcards.
    Example: "btc*"
    Default value: "*" (all available pairs)
"""

    if md_summary and not show_summary:
        print(
            f"Error: '-m', '--markdown' option only works with '-s', '--summary'",
            file=sys.stderr)
        return 1

    if show_version:
        print(version)
        return

    if show_weighing:
        if show_json:
            print(weighing.as_json)
        else:
            print()
            print(weighing)
            print()
        return

    if show_computed_pairs:
        show_computed_pairs_fromula()
        return 

    if coinpairs_filter:
        coinpairs = get_coin_pairs(coinpairs_filter)
    else:
        coinpairs = ALL
    if not coinpairs:
        print(
            f"The {repr(coinpairs_filter)} filter did not return any results.",
            file=sys.stderr)
        return 1
    
    if show_summary:
        summary(coinpairs, md_summary)
        return

    data = {}

    get_price(
        coinpairs,
        ignore_zero_weighing=not(not_ignore_zero_weighing),
        detail=data,
        serializable=show_json)

    if show_json:
        print(json.dumps(data, indent=4, sort_keys=True))
        return

    def format_time(t):
        return '{}s'.format(round(t.seconds + t.microseconds/1000000, 2))

    time   = data['time']
    prices = data['prices']
    values = data['values']

    table=[]
    prices_count = {}
    for p in prices:
        row = []
        row.append(p["coinpair"].from_.name)
        row.append(p["coinpair"].to_.name)
        row.append(p["coinpair"].variant)
        row.append(p["description"])
        if not p["coinpair"] in prices_count:
            prices_count[p["coinpair"]] = 0
        prices_count[p["coinpair"]] += 1
        if p["ok"]:
            unit = 'p'
            v = p['price'] * (1000**4)
            if v > 1000:
                for unit in ['p', 'µ', 'm', ' ', 'K', 'M', 'G']:
                    v = v/1000
                    if v<1000:
                        break
            row.append(f"{p['coinpair'].to_.small_symbol} {v:9.5f}{unit}")
        else:
            row.append(trim(p["error"], 20))
        row.append(round(p["weighing"], 2))
        if p["percentual_weighing"]:
            row.append(round(p[
                "percentual_weighing"]*100, 1))
        else:
            row.append('N/A')
        if p["time"]:
            row.append(format_time(p["time"]))
        else:
            row.append('N/A')
        table.append(row)
    if table:
        table.sort(key=str)
        print()
        print(tabulate(table, headers=[
            'From', 'To', 'V.', 'Exchnage', 'Response', 'Weight', '%', 'Time'
        ]))

    table=[]
    for coinpair, d in values.items():
        row = []
        if 'prices' in d:
            row.append('↓')
        else:
            row.append('ƒ')
        row.append(coinpair)
        row.append(d['median_price'])
        row.append(d['mean_price'])
        row.append(d['weighted_median_price'])
        if 'prices' in d:
            if 'ok_sources_count' in d:
                row.append(f"{d['ok_sources_count']} of {prices_count[coinpair]}")
            else:
                row.append(len(d['prices']))
        else:
            row.append('N/A')
        row.append('✓' if d['ok'] else '✕')
        table.append(row)
    if table:
        table.sort(key=lambda x: str(x[1]))
        print()
        def dec_to_str(f):
            if not isinstance(f, Decimal):
                return f
            out = f"{f:,.6f}"
            if out=="0.000000":
                out = f"{f}"
                out = out.split('E-')
                out[1] = ''.join(["⁰¹²³⁴⁵⁶⁷⁸⁹"[int(i)] for i in out[1]])
                out = f"{float(out[0]):.3f} × 10⁻{out[1]}"                
            return out
        table = [[dec_to_str(f) for f in l] for l in table]
        print(tabulate(table,
            headers=['', 'Coin pair', 'Mediam', 'Mean',
                     'Weighted median', 'Sources', 'Ok' ],
            colalign=['center', 'left', 'right', 'right',
                      'right', 'center', 'center']))

    errors = []
    for p in prices:
        if not p["ok"] and p['weighing']:
            errors.append((f"Source {p['name']}", p["error"]))
    for k, v in values.items():
        if 'error' in v and v["error"]:
            errors.append((f"Coinpair {k}", v["error"]))    

    if errors:
        print()
        print("Errors detail")
        print("------ ------")
        for e in errors:
            print()
            print('{}: {}'.format(*e))

    print()
    print('Response time {}'.format(format_time(time)))
    print()



if __name__ == '__main__':
    exit(cli_check())
