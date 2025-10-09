#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SeeTrain 命令行接口
"""

import argparse
import sys
from typing import Optional


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="SeeTrain - 深度学习实验跟踪和框架集成工具",
        prog="seetrain"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 初始化命令
    init_parser = subparsers.add_parser("init", help="初始化实验")
    init_parser.add_argument("--project", required=True, help="项目名称")
    init_parser.add_argument("--experiment", required=True, help="实验名称")
    init_parser.add_argument("--description", help="实验描述")
    init_parser.add_argument("--framework", help="深度学习框架")
    
    # 版本命令
    version_parser = subparsers.add_parser("version", help="显示版本信息")
    
    # 帮助命令
    help_parser = subparsers.add_parser("help", help="显示帮助信息")
    
    args = parser.parse_args()
    
    if args.command == "init":
        print(f"初始化实验: {args.project}/{args.experiment}")
        if args.description:
            print(f"描述: {args.description}")
        if args.framework:
            print(f"框架: {args.framework}")
        print("实验已初始化！")
        
    elif args.command == "version":
        from . import __version__
        print(f"SeeTrain version {__version__}")
        
    elif args.command == "help":
        parser.print_help()
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
