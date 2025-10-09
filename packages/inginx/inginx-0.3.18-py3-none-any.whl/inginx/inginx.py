#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory

CONFIG = """
daemon off;
worker_processes 1;
error_log /dev/stderr;

pid pid;
events {}

http {
    error_log stderr;
    access_log /dev/stdout;
    
    $SERVER
}
"""

SERVER_ECHO = """
server {
    listen $LISTEN;

    location / {
        return 200 $http_user_agent;
    }
}
"""

SERVER_SERVE_DIR = """
server {
    listen $LISTEN;

    location / {
        include  /etc/nginx/mime.types;
        autoindex on;
        root $ROOT;
    }
}
"""

SERVER_PROXY_PASS = """
server {
    listen $LISTEN;
    proxy_ssl_server_name on;

    location / {
        proxy_pass $UPSTREAM;
    }
}
"""

def find_default_executable():
    for candidate in ("freenginx", "nginx"):
        path = shutil.which(candidate)
        if path:
            return path
    return None



def main():
    # formatter_class because breaking lines caused the links in help to break
    parser = argparse.ArgumentParser(
            prog='inginx', 
            description='Spawn single use nginx instances. Default behavior is the same as --serve $(pwd)', 
            formatter_class=argparse.RawTextHelpFormatter
            )

    # TODO none of this is implemented
    parser.add_argument("-e", "--executable", metavar="executable", help="Which nginx executable to use. By default will try freenginx, nginx, in this order")
    parser.add_argument("-p", "--prefix", metavar="directory", help="What directory to use as nginx prefix. By default will use tempfile.TemporaryDirectory")

    parser.add_argument("-s", "--serve", metavar="directory", help="Use to setup a filesystem directory. Will be pasted directly into the root directive https://freenginx.org/en/docs/http/ngx_http_core_module.html#root")
    parser.add_argument("-r", "--reverse", metavar="remote", help="Use to setup a reverse proxy. Will be pasted directly into the proxy_pass directive https://freenginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass")
    parser.add_argument("-c", "--echo", action="store_true", help="Use to setup an echo http server")
    parser.add_argument("-l", "--listen", metavar="address[:port]", default="0.0.0.0:8888", help="What address to listen to. Will be pasted directly into the listen directive https://freenginx.org/en/docs/http/ngx_http_core_module.html#listen")

    parser.add_argument("-d", "--dry", action="store_true", help="Construct the config, print it, and exit.")
    parser.add_argument("-t", "--test", action="store_true", help="Construct the config, run nginx test on it and exit")

    args = parser.parse_args()

    assert not (args.dry and args.test), "Do not specify --dry and --test at the same time"
    assert not (args.serve and args.reverse), "Do not specify --serve and --reverse at the same time"

    executable = args.executable or find_default_executable()

    with (TemporaryDirectory(delete=False) if not args.prefix else nullcontext(args.prefix)) as d:

        try:
            d = Path(d).absolute()
            d.mkdir(parents=True, exist_ok=True)

            config_content = CONFIG

            action = ""

            if args.reverse:
                config_content = config_content.replace("$SERVER", SERVER_PROXY_PASS)
                config_content = config_content.replace("$UPSTREAM", args.reverse)
                action = f"reverse proxying {args.reverse}"
            if args.echo:
                config_content = config_content.replace("$SERVER", SERVER_ECHO)
                action = f"http echoing"
            else:
                config_content = config_content.replace("$SERVER", SERVER_SERVE_DIR)
                serve = str(Path(args.serve or os.getcwd()).absolute())
                config_content = config_content.replace("$ROOT", serve)
                action = f"serving files {serve} directory"

            config_content = config_content.replace("$LISTEN", args.listen)

            conf_path = d / "nginx.conf"
            with open(conf_path, "w") as f:
                f.write(config_content)

            if args.dry:
                print(config_content)
                return

            nginx_args = [executable, "-c", str(conf_path), "-p", str(d)]

            if args.test:
                nginx_args.append("-t")

            print(f"{' '.join(nginx_args)}", file=sys.stderr)
            print(action + f" listening on http://{args.listen}")
            nginx = subprocess.call(nginx_args)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
