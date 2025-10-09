#!/usr/bin/env python3
"""
Main entry point for coin-counter package.
Routes to CLI or GUI based on command-line arguments.
"""
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description='Coin Counter - Detect and identify coins',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  coin-counter-cli register --label Quarter --value 0.25 --front q_f.jpg --back q_b.jpg
  coin-counter-cli detect --scene coins.jpg
  coin-counter-gui
        """
    )
    parser.add_argument('--cli', action='store_true', 
                        help='Run CLI version')
    parser.add_argument('--gui', action='store_true',
                        help='Run GUI version')

    args, remaining = parser.parse_known_args()

    try:
        if args.cli:
            print("Running CLI version...")
            coin-counter-cli
        elif args.gui:
            print("Running GUI version...")
            coin-counter-gui
        else:
            print("Please specify either --cli or --gui.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()