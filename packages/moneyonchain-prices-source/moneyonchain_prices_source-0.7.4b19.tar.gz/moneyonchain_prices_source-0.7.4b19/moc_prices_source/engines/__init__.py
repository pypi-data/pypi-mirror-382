import concurrent.futures, sys
from os       import listdir, path
from os.path  import isfile, dirname, abspath

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))


all_engines     = {}
session_storage = {}
exclude         = ['engine_base.py', 'coins.py']
files           = [f for f in listdir(base_dir) if isfile(path.join(base_dir, f))]
files           = [f for f in files if f not in exclude]
modules_names   = [ n[:-3] for n in files if n[-3:] =='.py' and n[:1]!='_']

del listdir, path, isfile, dirname, files, exclude

sys.path.append(base_dir)
sys.path = sorted(list(set(sys.path[:])), key = lambda x: [
    'moc_prices_source/engines' in x, x], reverse=True)

for name in modules_names:
    locals()[name] = __import__(name, globals(), locals()).Engine(session_storage=session_storage)
    all_engines[name] = locals()[name]
    
sys.path = bkpath

del name, modules_names



def get_coinpair_list():
    engines_list = all_engines.values()
    coinpair_list = [ engine.coinpair for engine in engines_list ]
    coinpair_list = list(set(coinpair_list))
    coinpair_list.sort()
    return coinpair_list



def get_engines_names():
    engines_list = all_engines.values()
    engines_names = [ engine.name for engine in engines_list ]
    engines_names.sort()
    return engines_names



def get_prices(coinpairs=None, engines_names=None, engines_list=None):

    if engines_list is None: 
        engines_list = []

    assert isinstance(engines_list, (list, str))
    if not engines_list:
        engines_list = all_engines.values()

    if engines_names:
        assert isinstance(engines_names, (list, str))
        engines_list = [ e for e in engines_list if (
            e.name in engines_names or e.description in engines_names) ]

    if coinpairs:
        assert isinstance(coinpairs, (list, str))
        engines_list = [ e for e in engines_list if (
            e.coinpair in coinpairs) ]

    if not engines_list:
        return []

    ##########################################################################
    # FIXME! I need to figure out a better fix for this. I replace this:     #
    #                                                                        #
    # with concurrent.futures.ThreadPoolExecutor(                            #
    #     max_workers=len(engines_list)) as executor:                        #
    #     concurrent.futures.wait([ executor.submit(engine                   #
    #         ) for engine in engines_list ] )                               #
    #                                                                        #
    # for this:                                                              #
    #                                                                        #

    stack = engines_list[:]
   
    while stack:
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(stack)
                                                   ) as executor:
            concurrent.futures.wait(
                [ executor.submit(engine) for engine in stack ])

        new_stack = []
        
        for engine in engines_list:
            d = engine.as_dict
            if not(d['price']) and d['ok']:
                new_stack.append(engine)
        stack = new_stack

    #                                                                        #
    ##########################################################################

    return [ engine.as_dict for engine in engines_list ]



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    for data in get_prices():
        print()
        print('{}:'.format(data['name']))
        print()
        for key, value in data.items():
            if key!='name':
                print('    {} = {}'.format(key, value))
    print()