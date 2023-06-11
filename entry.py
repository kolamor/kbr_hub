import asyncio

import uvicorn

import argparse
import logging
from src.settings import load_config
from src.app import create_app


parser = argparse.ArgumentParser(description='kbrd app')
parser.add_argument('--host', help='Host to listen', default='0.0.0.0')
parser.add_argument('--port', help='Port to accept connections', default='5000')
parser.add_argument('--reload',
                    action='store_true',
                    help='Autoreload code on change')
parser.add_argument('-c', '--config', type=argparse.FileType('r'),
                    help='Path to configuration yaml file')
args = parser.parse_args()
config = load_config(args.config)
app = create_app(config=config)

if args.reload:
    print('Start with code reload')


def setup_logging():
    logging.basicConfig(level=config.LOG_LEVEL,
                        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")


if __name__ == '__main__':
    setup_logging()
    app = create_app(config=config)
    # try:
    #     import aiomonitor
    #     loop = asyncio.get_event_loop()
    #     with aiomonitor.start_monitor(loop=loop,
    #                                   # locals= {"port": args.port, "host": args.host}
    #                                   ):
    #         uvicorn.run(app, host=args.host, port=int(args.port), reload=args.reload)
    # except ImportError:
    #     uvicorn.run(app, host=args.host, port=int(args.port), reload=args.reload)
    uvicorn.run(f'{__name__}:app', host=args.host, port=int(args.port), reload=bool(args.reload))
