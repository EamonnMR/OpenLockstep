#!/usr/bin/python3

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs OpenLockstep')
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--client', action='store_true')

    args = parser.parse_args()

    if args.client:
        print("OLS Client Init")
    if args.server:
        print("OLS Server Init")
