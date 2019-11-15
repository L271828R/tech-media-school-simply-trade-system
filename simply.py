from com.core import simply_core
import sys
import argparse


if __name__ == '__main__':
    conf = {
            'db_location':"db/trade.db",
            'log_location':'logs',
            'cash_validation':False,
            'is_prod':True
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("--cash_validation")
    parser.add_argument("--is_prod")
    args = vars(parser.parse_args(sys.argv[1:]))
    if args['cash_validation'] is not None:
        conf['cash_validation'] = args['cash_validation']


    if args['is_prod'] is not None:
        conf['is_prod'] = args['is_prod']


    # print(args)
    # print(conf)
    simply_core.run(conf)



