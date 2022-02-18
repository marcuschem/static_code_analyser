import argparse
from checker import static_analyzer


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("files_path")
    args = parser.parse_args()
    return static_analyzer(args.files_path)


if __name__ == "__main__":
    main()