#!/usr/bin/python3

import argparse

import net

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs OpenLockstep')
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--client', action='store_true')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--clients', type=int, default=1)

    args = parser.parse_args()
    if args.client:
        client = net.Client(args.host, args.port)
        while True:
            text = input("> ")[:255]
            client.send(bytes([len(text)]))
            client.send(text.encode('utf-8'))
    elif args.server:
        net.Server(args.port, host=args.host, client_count=args.clients).run()


