"""MySensors adapter for Mozilla WebThings Gateway."""

from os import path
import functools
import gateway_addon
import signal
import sys
import time
import asyncio
import json
import tracemalloc

tracemalloc.start()


DIRNAME = path.dirname(path.abspath(__file__))

sys.path.append(path.join(DIRNAME, 'lib'))

from pkg.mysensors_adapter import MySensorsAdapter, ConfigLoader

_API_VERSION = {
    'min': 2,
    'max': 2,
}
_ADAPTERS = []

print = functools.partial(print, flush=True)


def cleanup(signum, frame):
    """Clean up any resources before exiting."""
    for adapter in _ADAPTERS:
        adapter.close_proxy()

    sys.exit(0)


if __name__ == '__main__':
    if gateway_addon.API_VERSION < _API_VERSION['min'] or \
            gateway_addon.API_VERSION > _API_VERSION['max']:
        print('Unsupported API version.')
        sys.exit(0)

    loop = asyncio.get_event_loop()

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    package_name = json.load(open(path.join(DIRNAME, 'manifest.json'), 'r'))['id']
    loader = ConfigLoader()
    config = loader.load_config(package_name)

    for i, config in enumerate(config.get('gateways', [])):
        instance_id = package_name + '-' + str(i)
        _ADAPTERS.append(MySensorsAdapter(instance_id, package_name, config, verbose=False))

    loop.run_forever()