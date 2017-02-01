# coding: utf-8

import os
import sys

if not sys.implementation.name == 'micropython':
    sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'shared')))

# noinspection PyPep8,PyUnresolvedReferences
import config
# noinspection PyPep8,PyUnresolvedReferences
import commander

if config.IS_MICROPYTHON:
    # noinspection PyUnresolvedReferences
    import worker_upython as worker_impl
    # import worker_neuron as worker_impl    
else:
    # noinspection PyUnresolvedReferences
    import worker_cpython as worker_impl


class Node(commander.Commander):
    # @profile(precision=4)
    def __init__(self):
        super().__init__()
        self.worker = worker_impl.Worker(config.BROKER_HOST, config.HUB_PORT)
        self.worker.set_parent(self)

    # @profile(precision=4)
    def run(self):
        self.worker.run()

    # @profile(precision=4)
    def stop(self):
        self.worker.stop()
        self.worker.set_parent(None)

    # @profile(precision=4)
    def request(self, **message):
        return self.worker.request(message)


def main():
    try:
        node = Node()
        node.run()

    except KeyboardInterrupt:
        print("Ctrl C - Stopping.")
        # noinspection PyUnboundLocalVariable
        node.stop()
        # noinspection PyUnusedLocal
        node = None
        sys.exit(1)


if __name__ == '__main__':
    main()
