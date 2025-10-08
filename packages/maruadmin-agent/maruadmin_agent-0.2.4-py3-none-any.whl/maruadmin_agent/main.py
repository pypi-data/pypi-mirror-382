"""
MaruAdmin Agent main entry point
"""
import argparse
import signal
import sys
import time
from pathlib import Path

from .command_handler import CommandHandler
from .config import get_config, load_config
from .monitor import AgentRegistration, SystemMonitor
from .ssh_server import SSHServer
from .utils import get_agent_id, setup_logging


class MaruAdminAgent:
    """Main agent class"""

    def __init__(self, config_path: str = None):
        """Initialize agent"""
        # Load configuration
        self.config = load_config(config_path)

        # Generate or get agent ID
        if not self.config.agent_id:
            self.config.agent_id = get_agent_id()

        # Setup logging
        self.logger = setup_logging(self.config.log_file, self.config.log_level)
        self.logger.info("MaruAdmin Agent starting...")
        self.logger.info(f"Agent ID: {self.config.agent_id}")
        self.logger.info(f"Agent Name: {self.config.agent_name}")

        # Initialize components
        self.command_handler = CommandHandler(self.config, self.logger)
        self.ssh_server = SSHServer(self.config, self.command_handler, self.logger)
        self.system_monitor = SystemMonitor(self.config, self.logger)

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

        self.running = False

    def handle_signal(self, signum, frame):
        """Handle system signals"""
        self.logger.info(f"Received signal {signum}")
        self.stop()

    def register(self) -> bool:
        """Register agent with server"""
        self.logger.info("Registering agent with server...")
        return AgentRegistration.register_agent(self.config, self.logger)

    def start(self) -> None:
        """Start agent services"""
        if self.running:
            return

        self.running = True
        self.logger.info("Starting agent services...")

        # Register with server
        if self.config.api_url and self.config.api_token:
            if not self.register():
                self.logger.warning("Failed to register with server, continuing anyway...")

        # Start SSH server
        self.ssh_server.start()

        # Start system monitoring
        if self.config.api_url:
            self.system_monitor.start()

        self.logger.info("Agent services started")

    def stop(self) -> None:
        """Stop agent services"""
        if not self.running:
            return

        self.running = False
        self.logger.info("Stopping agent services...")

        # Stop components
        self.system_monitor.stop()
        self.ssh_server.stop()

        self.logger.info("Agent services stopped")

    def run(self) -> None:
        """Run agent main loop"""
        self.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

        self.stop()
        self.logger.info("Agent exited")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='MaruAdmin Agent')
    parser.add_argument(
        '-c', '--config',
        help='Configuration file path',
        default='/etc/maruadmin/agent.conf'
    )
    parser.add_argument(
        '--register',
        action='store_true',
        help='Register agent and exit'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test configuration and exit'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='MaruAdmin Agent 0.1.0'
    )

    args = parser.parse_args()

    # Test configuration
    if args.test:
        try:
            config = load_config(args.config)
            print("Configuration is valid")
            print(f"Agent ID: {config.agent_id or get_agent_id()}")
            print(f"Agent Name: {config.agent_name}")
            print(f"API URL: {config.api_url}")
            print(f"SSH Port: {config.ssh_port}")
            sys.exit(0)
        except Exception as e:
            print(f"Configuration error: {e}")
            sys.exit(1)

    # Register only
    if args.register:
        config = load_config(args.config)
        if not config.agent_id:
            config.agent_id = get_agent_id()

        logger = setup_logging(config.log_file, config.log_level)

        if AgentRegistration.register_agent(config, logger):
            print("Agent registered successfully")
            sys.exit(0)
        else:
            print("Agent registration failed")
            sys.exit(1)

    # Run agent
    try:
        agent = MaruAdminAgent(args.config)
        agent.run()
    except Exception as e:
        print(f"Agent error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()