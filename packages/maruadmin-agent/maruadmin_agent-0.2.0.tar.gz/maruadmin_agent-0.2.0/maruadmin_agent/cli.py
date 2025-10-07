#!/usr/bin/env python3
"""
MaruAdmin Agent CLI tool for executing commands
"""
import sys
import json
import argparse

from .command_handler import CommandHandler
from .config import load_config
from .utils import setup_logging


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description='MaruAdmin Agent CLI')
    parser.add_argument('command_json', help='Command JSON string')
    parser.add_argument('-c', '--config', default='/etc/maruadmin/agent.conf',
                        help='Configuration file path')

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)

        # Setup logging
        logger = setup_logging(config.log_file, config.log_level)

        # Parse command
        command = json.loads(args.command_json)

        # Create command handler
        handler = CommandHandler(config, logger)

        # Execute command
        result = handler.handle_command(command)

        # Output result as JSON
        print(json.dumps(result))

        # Exit with success/failure code
        sys.exit(0 if result.get('success') else 1)

    except json.JSONDecodeError:
        print(json.dumps({
            'success': False,
            'error': 'Invalid JSON command'
        }))
        sys.exit(1)

    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }))
        sys.exit(1)


if __name__ == '__main__':
    main()
