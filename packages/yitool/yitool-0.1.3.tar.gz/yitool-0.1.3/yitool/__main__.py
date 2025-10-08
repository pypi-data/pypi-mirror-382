# -*- coding: utf-8 -*-
"""命令行入口"""

from yitool.cli import Cli

def main():
    Cli.parse_config_file()
    cli = Cli()
    cli()

if __name__ == "__main__":
    main()