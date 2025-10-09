import asyncio
import pathlib
import mimetypes
import logging
import random

from websockets.server import serve

import wisp
from wisp.server import connection
from wisp.server import ratelimit
from wisp.server import net

async def connection_handler(websocket, path):
  client_ip = websocket.remote_address[0]
  if client_ip == "127.0.0.1" and "X-Real-IP" in websocket.request_headers:
    client_ip = websocket.request_headers["X-Real-IP"]
  origin = websocket.request_headers.get("Origin")

  conn_id = "".join(random.choices("1234567890abcdef", k=8))
  logging.info(f"({conn_id}) incoming connection on {path} from {client_ip} (origin: {origin})")
  ratelimit.inc_client_attr(client_ip, "streams")

  if path.endswith("/"):
    wisp_conn = connection.WispConnection(websocket, path, client_ip, conn_id)
    await wisp_conn.setup()
    ws_handler = asyncio.create_task(wisp_conn.handle_ws()) 
    await asyncio.gather(ws_handler)

  else:
    stream_count = ratelimit.get_client_attr(client_ip, "streams")
    if ratelimit.enabled and stream_count > ratelimit.connections_limit:
      return
    wsproxy_conn = connection.WSProxyConnection(websocket, path, client_ip)
    await wsproxy_conn.setup_connection()
    ws_handler = asyncio.create_task(wsproxy_conn.handle_ws())
    tcp_handler = asyncio.create_task(wsproxy_conn.handle_tcp())
    await asyncio.gather(ws_handler, tcp_handler)

async def static_handler(path, request_headers):
  if "Upgrade" in request_headers:
    return
    
  response_headers = []
  target_path = static_path / path[1:]

  if target_path.is_dir():
    target_path = target_path / "index.html"
  if not target_path.is_relative_to(static_path):
    return 403, response_headers, "403 forbidden".encode()
  if not target_path.exists():
    return 404, response_headers, "404 not found".encode()
  
  mimetype = mimetypes.guess_type(target_path.name)[0]
  response_headers.append(("Content-Type", mimetype))

  static_data = await asyncio.to_thread(target_path.read_bytes)
  return 200, response_headers, static_data

async def main(args):
  global static_path

  if args.static:
    static_path = pathlib.Path(args.static).resolve()
    request_handler = static_handler
    mimetypes.init()
  else:
    request_handler = None
  
  if args.limits:
    ratelimit.enabled = True
    ratelimit.connections_limit = int(args.connections)
    ratelimit.bandwidth_limit = float(args.bandwidth)
    ratelimit.window_size = float(args.window)
  
  if args.proxy:
    if args.proxy.startswith("socks5h:"):
      net.proxy_url = args.proxy.replace("socks5h:", "socks5:", 1)
      net.proxy_dns = True
    elif args.proxy.startswith("socks4a:"):
      net.proxy_url = args.proxy.replace("socks4a:", "socks4:", 1)
      net.proxy_dns = True
    else:
      net.proxy_url = args.proxy
      net.proxy_dns = False

  net.block_loopback = not args.allow_loopback
  net.block_private = not args.allow_private
  net.block_udp = args.block_udp
  net.block_tcp = args.block_tcp
      
  limit_task = asyncio.create_task(ratelimit.reset_limits_timer())
  ws_logger = logging.getLogger("websockets")
  ws_logger.setLevel(logging.WARN)

  reuse_port = net.reuse_port_supported()
  server_header = f"wisp-server-python v{wisp.version}"

  async with serve(
    connection_handler, args.host, int(args.port), 
    reuse_port=reuse_port, process_request=request_handler, 
    compression=None, server_header=server_header
  ):
    await asyncio.Future()