#!/usr/bin/env python3
"""
Sphinx Headless Python Wrapper

This script starts a Jupyter server and invokes the Sphinx headless CLI
to connect to that server for AI-powered Jupyter notebook interactions.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional

import shutil
import urllib.request
import urllib.error

import backoff


def check_jupyter_dependencies() -> None:
    """Check if required dependencies for Jupyter server are installed."""
    missing_deps = []
    
    # Check for jupyter server
    try:
        import jupyter_server
    except ImportError:
        missing_deps.append("jupyter-server")
    
    # Check for ipykernel (needed for kernel management)
    try:
        import ipykernel
    except ImportError:
        missing_deps.append("ipykernel")
    
    if missing_deps:
        deps_str = " ".join(missing_deps)
        raise ImportError(
            f"Missing required dependencies for Jupyter server: {deps_str}\n"
            f"Please install them with: pip install {deps_str}\n"
        )



def run_sphinx_chat(
    notebook_filepath: str,
    prompt: str,
    *,
    sphinx_url: str = "https://api.prod.sphinx.ai",
    jupyter_server_url: Optional[str] = None,
    jupyter_server_token: Optional[str] = None,
    jupyter_server_port: int = 8888,
    verbose: bool = False,
    no_memory_read: bool = False,
    no_memory_write: bool = False,
    no_package_installation: bool = False,
    no_collapse_exploratory_cells: bool = False,
    sphinx_rules_path: Optional[str] = None
) -> int:
    """
    Run a Sphinx chat session with an embedded Jupyter server.

    Args:
        sphinx_url: The URL of the Sphinx service
        notebook_filepath: Path to the notebook file
        prompt: Prompt to create a thread
        jupyter_server_url: URL of existing Jupyter server (if None, will start new server)
        jupyter_server_token: Token for existing Jupyter server (if None, will generate new token)
        jupyter_server_port: Port for the Jupyter server (only used if starting new server)
        verbose: Whether to print status messages

    Returns:
        Exit code from the headless CLI (0 for success)
    """
    # Validate notebook file exists
    notebook_path = Path(notebook_filepath)
    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook file not found: {notebook_path}")
    
    # Check dependencies if we need to start a Jupyter server
    if jupyter_server_url is None:
        if verbose:
            print("🔍 Checking Jupyter server dependencies...")
        try:
            check_jupyter_dependencies()
            if verbose:
                print("✅ Jupyter server dependencies are available")
        except ImportError as e:
            print(f"❌ {e}")
            return 1
    
    jupyter_process = None
    temp_dir = None
    jupyter_token = None
    server_url = None
    
    try:
        # Determine if we should use an existing server or start a new one
        if jupyter_server_url is not None:
            # Use existing server
            # Normalize the URL format
            if not jupyter_server_url.startswith(('http://', 'https://')):
                # Assume localhost if no protocol specified
                if ':' in jupyter_server_url:
                    server_url = f"http://{jupyter_server_url}"
                else:
                    server_url = f"http://{jupyter_server_url}:8888"
            else:
                server_url = jupyter_server_url
            
            jupyter_token = jupyter_server_token
            
            if verbose:
                print(f"🔗 Using existing Jupyter server: {server_url}")
                if jupyter_token:
                    print(f"🔑 Using token: {jupyter_token[:8]}...")
            
            # Test the existing server
            if verbose:
                print("⏳ Testing existing Jupyter server...")
            
            def _probe(url: str) -> str:
                try:
                    with urllib.request.urlopen(url, timeout=10) as resp:
                        return f"OK {resp.status}"
                except urllib.error.HTTPError as e:
                    return f"HTTP {e.code}"
                except Exception as e:
                    return f"ERR {type(e).__name__}: {e}"
            
            # Test server with token if provided
            test_url = f"{server_url}/api/status"
            if jupyter_token:
                test_url = f"{server_url}/api/status?token={jupyter_token}"
            
            if verbose:
                print(f"🧪 Testing: {test_url}")
            
            status_try = _probe(test_url)
            if verbose:
                print(f"🧪 Response: {status_try}")
            
            if not status_try.startswith("OK 200"):
                raise RuntimeError(f"Existing Jupyter server is not accessible: {status_try}\n"
                                 f"Please check:\n"
                                 f"1. Server is running at {server_url}\n"
                                 f"2. Token is correct (if provided)\n"
                                 f"3. Server allows connections from this host")
            
            if verbose:
                print("✅ Existing Jupyter server is ready")
        else:
            # Start a new Jupyter server
            if verbose:
                print("🚀 Starting new Jupyter server...")
            
            # Create a temporary directory for Jupyter runtime
            temp_dir = tempfile.mkdtemp(prefix="sphinx_jupyter_")
            
            # Generate a known token for the Jupyter server
            import secrets
            jupyter_token = secrets.token_hex(32)
            
            # Start Jupyter server (not notebook/lab) with proper configuration
            # Use sys.executable to ensure we use the same Python environment
            jupyter_process = subprocess.Popen([
                sys.executable, "-m", "jupyter", "server", 
                "--no-browser",
                f"--port={jupyter_server_port}",
                f"--ServerApp.token={jupyter_token}",
                f"--ServerApp.runtime_dir={temp_dir}",
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=temp_dir)
            
            # Actively wait for Jupyter to become ready
            if verbose:
                print("⏳ Waiting for Jupyter server readiness...")

            def _probe(url: str) -> str:
                try:
                    with urllib.request.urlopen(url, timeout=5) as resp:
                        return f"OK {resp.status}"
                except urllib.error.HTTPError as e:
                    return f"HTTP {e.code}"
                except Exception as e:
                    return f"ERR {type(e).__name__}: {e}"

            base = f"http://localhost:{jupyter_server_port}"
            server_url = base

            @backoff.on_exception(backoff.expo, Exception, max_time=15)
            def check_ready():
                # If the server process crashed, surface logs and abort early
                if jupyter_process.poll() is not None:
                    try:
                        err = jupyter_process.stderr.read().decode(errors='ignore')
                    except Exception:
                        err = "<no stderr available>"
                    raise RuntimeError(f"Jupyter server exited early with code {jupyter_process.returncode}. Stderr:\n{err}")
                # try status with token
                status_try = _probe(f"{base}/api/status?token={jupyter_token}")
                if verbose:
                    print(f"🧪 /api/status => {status_try}")
                if not status_try.startswith("OK 200"):
                    raise Exception(f"Jupyter server is not ready: {status_try}")

            check_ready()

            if verbose:
                print("✅ Jupyter server is ready")
                print(f"🔗 Server URL: {server_url}")
        
        # Convert notebook path to absolute path
        notebook_abs_path = str(Path(notebook_filepath).resolve())

        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        
        # Look for the sphinx-cli.cjs file
        cjs_file = script_dir / "sphinx-cli.cjs"
        
        if not cjs_file.exists():
            raise FileNotFoundError("sphinx-cli.cjs not found")
        
        # Create a temporary directory for nodeenv
        with tempfile.TemporaryDirectory() as nodeenv_temp_dir:
            nodeenv_temp_path = Path(nodeenv_temp_dir)
            
            # Create nodeenv environment
            nodeenv_path = nodeenv_temp_path / "nodeenv"
            try:
                subprocess.run([
                    sys.executable, "-m", "nodeenv", str(nodeenv_path)
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error creating nodeenv: {e}")
            
            # Get the node executable path
            if os.name == 'nt':  # Windows
                node_exe = nodeenv_path / "Scripts" / "node.exe"
            else:  # Unix-like
                node_exe = nodeenv_path / "bin" / "node"

            node_args = [
                "chat",
                "--jupyter-server-url", server_url,
                "--sphinx-url", sphinx_url,
                "--notebook-filepath", notebook_abs_path,
                "--prompt", prompt,
            ]
            
            # Only add token if we have one
            if jupyter_token:
                node_args.extend(["--jupyter-server-token", jupyter_token])

            if no_memory_read:
                node_args.append("--no-memory-read")

            if no_memory_write:
                node_args.append("--no-memory-write")

            if no_package_installation:
                node_args.append("--no-package-installation")

            if no_collapse_exploratory_cells:
                node_args.append("--no-collapse-exploratory-cells")

            if sphinx_rules_path:
                node_args.append(f"--sphinx-rules-path={sphinx_rules_path}")
            
            # Run the sphinx-cli.cjs with node
            cmd = [str(node_exe), str(cjs_file)] + node_args
            
            # Set environment variables for headless operation
            env = os.environ.copy()
            env.update({
                'DISPLAY': '',  # Disable X11 display
                'BROWSER': 'none',  # Disable browser opening
                'NO_BROWSER': '1',  # Alternative browser disable flag
                'HEADLESS': '1',  # Headless mode flag
            })
            
            if verbose:
                print(f"🔧 Invoking headless CLI: {' '.join(cmd)}")
                print(f"Environment: HEADLESS={env.get('HEADLESS')}, DISPLAY={env.get('DISPLAY')}")
                print(f"Working directory: {os.getcwd()}")
                print(f"Node.js executable: {node_exe}")
                print(f"CLI file: {cjs_file}")
            else:
                print("Starting Node.js process...")
            
            # Use Popen to stream output in real-time
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                env=env,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Stream output in real-time
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    print(line)
                    output_lines.append(line)
            
            # Wait for process to complete and get return code
            return_code = process.wait()
            
            # If process failed and we have no output, provide helpful error info
            if return_code != 0 and not output_lines:
                print(f"❌ Process failed with exit code {return_code}")
                print("No output was captured. This might indicate:")
                print("1. The sphinx-cli.cjs file is not executable")
                print("2. Node.js is not properly installed in the nodeenv")
                print("3. The CLI command failed silently")
                if verbose:
                    print(f"Command that failed: {' '.join(cmd)}")
                    print(f"Working directory: {os.getcwd()}")
                # Try to get stderr for more info
                try:
                    stderr_output = process.stderr.read()
                    if stderr_output:
                        print(f"Stderr output: {stderr_output}")
                except:
                    pass
            
            return return_code
        
    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"❌ Headless CLI failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError as e:
        if verbose:
            print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        if verbose:
            print(f"❌ Error: {e}")
        return 1
    finally:
        # Cleanup - only stop server if we started it
        if jupyter_process:
            if verbose:
                print("🛑 Stopping Jupyter server...")
            try:
                jupyter_process.terminate()
                jupyter_process.wait(timeout=10)
            except Exception as e:
                if verbose:
                    print(f"⚠️  Warning: Error stopping Jupyter server: {e}")
                try:
                    jupyter_process.kill()
                except:
                    pass

        if temp_dir:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                if verbose:
                    print(f"⚠️  Warning: Error cleaning up temp directory: {e}")
        
        if verbose:
            print("✅ Cleanup completed")


def run_login(verbose: bool = False) -> int:
    """Run the login command."""
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        cjs_file = script_dir / "sphinx-cli.cjs"
        
        if not cjs_file.exists():
            raise FileNotFoundError("sphinx-cli.cjs not found")
        
        # Create a temporary directory for nodeenv
        with tempfile.TemporaryDirectory() as nodeenv_temp_dir:
            nodeenv_temp_path = Path(nodeenv_temp_dir)
            
            # Install nodeenv
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "nodeenv"
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error installing nodeenv: {e}")
            
            # Create nodeenv environment
            nodeenv_path = nodeenv_temp_path / "nodeenv"
            try:
                subprocess.run([
                    sys.executable, "-m", "nodeenv", str(nodeenv_path)
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error creating nodeenv: {e}")
            
            # Get the node executable path
            if os.name == 'nt':  # Windows
                node_exe = nodeenv_path / "Scripts" / "node.exe"
            else:  # Unix-like
                node_exe = nodeenv_path / "bin" / "node"
            
            # Run the login command
            cmd = [str(node_exe), str(cjs_file), "login"]
            
            if verbose:
                print(f"🔧 Running login command: {' '.join(cmd)}")
            
            # Set environment variables for headless operation
            env = os.environ.copy()
            env.update({
                'DISPLAY': '',  # Disable X11 display
                'BROWSER': 'none',  # Disable browser opening
                'NO_BROWSER': '1',  # Alternative browser disable flag
                'HEADLESS': '1',  # Headless mode flag
            })
            
            # Run the command and stream output in real-time
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                env=env,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Stream output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            # Wait for process to complete and get return code
            return_code = process.wait()
            return return_code
            
    except Exception as e:
        if verbose:
            print(f"❌ Login error: {e}")
        return 1


def run_logout(verbose: bool = False) -> int:
    """Run the logout command."""
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        cjs_file = script_dir / "sphinx-cli.cjs"
        
        if not cjs_file.exists():
            raise FileNotFoundError("sphinx-cli.cjs not found")
        
        # Create a temporary directory for nodeenv
        with tempfile.TemporaryDirectory() as nodeenv_temp_dir:
            nodeenv_temp_path = Path(nodeenv_temp_dir)
            
            # Install nodeenv
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "nodeenv"
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error installing nodeenv: {e}")
            
            # Create nodeenv environment
            nodeenv_path = nodeenv_temp_path / "nodeenv"
            try:
                subprocess.run([
                    sys.executable, "-m", "nodeenv", str(nodeenv_path)
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error creating nodeenv: {e}")
            
            # Get the node executable path
            if os.name == 'nt':  # Windows
                node_exe = nodeenv_path / "Scripts" / "node.exe"
            else:  # Unix-like
                node_exe = nodeenv_path / "bin" / "node"
            
            # Run the logout command
            cmd = [str(node_exe), str(cjs_file), "logout"]
            
            if verbose:
                print(f"🔧 Running logout command: {' '.join(cmd)}")
            
            # Set environment variables for headless operation
            env = os.environ.copy()
            env.update({
                'DISPLAY': '',  # Disable X11 display
                'BROWSER': 'none',  # Disable browser opening
                'NO_BROWSER': '1',  # Alternative browser disable flag
                'HEADLESS': '1',  # Headless mode flag
            })
            
            # Run the command and stream output in real-time
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                env=env,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Stream output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            # Wait for process to complete and get return code
            return_code = process.wait()
            return return_code
            
    except Exception as e:
        if verbose:
            print(f"❌ Logout error: {e}")
        return 1


def run_status(verbose: bool = False) -> int:
    """Run the status command."""
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        cjs_file = script_dir / "sphinx-cli.cjs"
        
        if not cjs_file.exists():
            raise FileNotFoundError("sphinx-cli.cjs not found")
        
        # Create a temporary directory for nodeenv
        with tempfile.TemporaryDirectory() as nodeenv_temp_dir:
            nodeenv_temp_path = Path(nodeenv_temp_dir)
            
            # Install nodeenv
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "nodeenv"
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error installing nodeenv: {e}")
            
            # Create nodeenv environment
            nodeenv_path = nodeenv_temp_path / "nodeenv"
            try:
                subprocess.run([
                    sys.executable, "-m", "nodeenv", str(nodeenv_path)
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error creating nodeenv: {e}")
            
            # Get the node executable path
            if os.name == 'nt':  # Windows
                node_exe = nodeenv_path / "Scripts" / "node.exe"
            else:  # Unix-like
                node_exe = nodeenv_path / "bin" / "node"
            
            # Run the status command
            cmd = [str(node_exe), str(cjs_file), "status"]
            
            if verbose:
                print(f"🔧 Running status command: {' '.join(cmd)}")
            
            # Set environment variables for headless operation
            env = os.environ.copy()
            env.update({
                'DISPLAY': '',  # Disable X11 display
                'BROWSER': 'none',  # Disable browser opening
                'NO_BROWSER': '1',  # Alternative browser disable flag
                'HEADLESS': '1',  # Headless mode flag
            })
            
            # Run the command and stream output in real-time
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                env=env,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Stream output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            # Wait for process to complete and get return code
            return_code = process.wait()
            return return_code
            
    except Exception as e:
        if verbose:
            print(f"❌ Status error: {e}")
        return 1


def main():
    """Main entry point for the Sphinx headless Python CLI."""
    parser = argparse.ArgumentParser(
        description="Sphinx Headless Python CLI - Start Jupyter server and invoke Sphinx headless CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Authentication commands
  python runner.py login
  python runner.py logout
  python runner.py status
  
  # Chat commands (requires authentication)
  python runner.py chat --notebook-filepath ./notebook.ipynb --prompt "Create a model to predict y from x"
  python runner.py chat --notebook-filepath ./notebook.ipynb --prompt "Analyze this data" --jupyter-server-url http://localhost:8888 --jupyter-server-token your_token_here
  
  # Using existing Jupyter server (URL formats supported):
  # - localhost:8888 (will be converted to http://localhost:8888)
  # - http://localhost:8888
  # - https://your-server.com:8888
        """
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='Authenticate with Sphinx (opens web browser)')
    login_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Logout command
    logout_parser = subparsers.add_parser('logout', help='Logout and clear stored tokens')
    logout_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check authentication status')
    status_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Start a chat session with Sphinx')
    
    # Required arguments for chat
    chat_parser.add_argument(
        "--notebook-filepath",
        required=True,
        help="Path to the notebook file"
    )
    chat_parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt to create a thread"
    )

    # Optional arguments for chat
    chat_parser.add_argument(
        "--sphinx-url",
        default="https://api.prod.sphinx.ai",
        help="The URL of the Sphinx service"
    )

    chat_parser.add_argument(
        "--jupyter-server-url",
        help="URL of existing Jupyter server (if not provided, will start a new server)"
    )

    chat_parser.add_argument(
        "--jupyter-server-token",
        help="Token for existing Jupyter server (required if using --jupyter-server-url)"
    )

    chat_parser.add_argument(
        '--no-memory-read',
        action='store_true',
        help='Disable memory read (default: enabled)'
    )

    chat_parser.add_argument(
        '--no-memory-write',
        action='store_true',
        help='Disable memory write (default: enabled)'
    )

    chat_parser.add_argument(
        '--no-package-installation',
        action='store_true',
        help='Disable package installation (default: enabled)'
    )

    chat_parser.add_argument(
        '--no-collapse-exploratory-cells',
        action='store_true',
        help='Disable collapsing exploratory cells (default: enabled)'
    )

    chat_parser.add_argument(
        '--sphinx-rules-path',
        help='Path to the Sphinx rules file'
    )

    chat_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Handle different commands
    if args.command == 'login':
        try:
            exit_code = run_login(verbose=args.verbose)
            sys.exit(exit_code)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == 'logout':
        try:
            exit_code = run_logout(verbose=args.verbose)
            sys.exit(exit_code)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == 'status':
        try:
            exit_code = run_status(verbose=args.verbose)
            sys.exit(exit_code)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == 'chat':
        try:
            exit_code = run_sphinx_chat(
                sphinx_url=args.sphinx_url,
                notebook_filepath=args.notebook_filepath,
                prompt=args.prompt,
                jupyter_server_url=args.jupyter_server_url,
                jupyter_server_token=args.jupyter_server_token,
                verbose=args.verbose,
                no_memory_read=args.no_memory_read,
                no_memory_write=args.no_memory_write,
                no_package_installation=args.no_package_installation,
                no_collapse_exploratory_cells=args.no_collapse_exploratory_cells,
                sphinx_rules_path=args.sphinx_rules_path
            )
            sys.exit(exit_code)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    else:
        # No command provided, show help
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
