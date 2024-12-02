import argparse

from stockcore.parameters import Parameters

def main(config_path):
    # Load the configuration file
    params = Parameters.from_json(config_path)
    print(params)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate the performance of a trading strategy')
    parser.add_argument('config', type=str, help='Path to the configuration file')
    args = parser.parse_args()
    main(args.config)