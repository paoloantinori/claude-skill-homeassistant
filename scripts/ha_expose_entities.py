#!/usr/bin/env python3
"""
Home Assistant Entity Exposure Tool

Expose or unexpose entities to the conversation agent (AI assistant).

Usage:
    # Expose a single entity
    python3 ha_expose_entities.py expose sensor.flex_d_status

    # Expose multiple entities
    python3 ha_expose_entities.py expose sensor.flex_d_status sensor.nas_status

    # Unexpose entities
    python3 ha_expose_entities.py unexpose sensor.old_sensor

    # List currently exposed entities
    python3 ha_expose_entities.py list

    # Check if specific entities are exposed
    python3 ha_expose_entities.py check sensor.flex_d_status sensor.nas_status

Environment Variables Required:
    HASS_SERVER - Home Assistant server URL (e.g., http://homeassistant.local:8123)
    HASS_TOKEN  - Long-lived access token

Dependencies:
    pip install websockets
"""

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, List

try:
    import websockets
except ImportError:
    print("ERROR: websockets package required. Install with: pip install websockets")
    sys.exit(1)


@dataclass
class HAConnection:
    """Home Assistant WebSocket connection."""

    ws: Any
    msg_id: int = 0

    def next_id(self) -> int:
        self.msg_id += 1
        return self.msg_id

    async def send(self, msg_type: str, **kwargs) -> dict:
        """Send a message and wait for response."""
        msg_id = self.next_id()
        msg = {"id": msg_id, "type": msg_type, **kwargs}
        await self.ws.send(json.dumps(msg))

        while True:
            response = json.loads(await self.ws.recv())
            if response.get("id") == msg_id:
                return response
            # Skip events and other messages
            if response.get("type") == "event":
                continue


async def connect() -> HAConnection:
    """Connect to Home Assistant WebSocket API."""
    server = os.environ.get("HASS_SERVER", "").replace("http://", "").replace("https://", "").replace(":8123", "")
    token = os.environ.get("HASS_TOKEN", "")

    if not server or not token:
        print("ERROR: HASS_SERVER and HASS_TOKEN environment variables required")
        print("  export HASS_SERVER=http://homeassistant.local:8123")
        print("  export HASS_TOKEN=your_token_here")
        sys.exit(1)

    uri = f"ws://{server}:8123/api/websocket"
    ws = await websockets.connect(uri)

    # Wait for auth_required
    await ws.recv()

    # Authenticate
    await ws.send(json.dumps({"type": "auth", "access_token": token}))
    auth_result = json.loads(await ws.recv())

    if auth_result.get("type") != "auth_ok":
        print(f"ERROR: Authentication failed: {auth_result}")
        sys.exit(1)

    return HAConnection(ws=ws)


async def get_exposed_entities(conn: HAConnection) -> dict:
    """Get all entities exposed to conversation agent."""
    # Get entity registry
    result = await conn.send("config/entity_registry/list")
    if not result.get("success"):
        print(f"ERROR: Failed to get entity registry: {result}")
        return {}

    exposed = {}
    for entity in result.get("result", []):
        entity_id = entity.get("entity_id", "")
        options = entity.get("options", {})
        conv_options = options.get("conversation", {})
        if conv_options.get("should_expose"):
            exposed[entity_id] = {
                "name": entity.get("name") or entity.get("original_name", ""),
                "area_id": entity.get("area_id"),
            }

    return exposed


async def expose_entities(conn: HAConnection, entity_ids: List[str], should_expose: bool) -> bool:
    """Expose or unexpose entities to conversation agent."""
    result = await conn.send(
        "homeassistant/expose_entity",
        assistants=["conversation"],
        entity_ids=entity_ids,
        should_expose=should_expose,
    )

    return result.get("success", False)


async def check_entities(conn: HAConnection, entity_ids: List[str]) -> dict:
    """Check exposure status of specific entities."""
    # Get entity registry
    result = await conn.send("config/entity_registry/list")
    if not result.get("success"):
        print(f"ERROR: Failed to get entity registry: {result}")
        return {}

    status = {}
    entity_map = {e.get("entity_id"): e for e in result.get("result", [])}

    for entity_id in entity_ids:
        if entity_id in entity_map:
            entity = entity_map[entity_id]
            options = entity.get("options", {})
            conv_options = options.get("conversation", {})
            status[entity_id] = {
                "exists": True,
                "exposed": conv_options.get("should_expose", False),
                "name": entity.get("name") or entity.get("original_name", ""),
            }
        else:
            status[entity_id] = {"exists": False, "exposed": False, "name": ""}

    return status


async def cmd_expose(args):
    """Handle expose command."""
    conn = await connect()
    try:
        success = await expose_entities(conn, args.entities, should_expose=True)
        if success:
            print(f"Successfully exposed {len(args.entities)} entity(ies) to conversation agent:")
            for entity_id in args.entities:
                print(f"  + {entity_id}")
        else:
            print("ERROR: Failed to expose entities")
            sys.exit(1)
    finally:
        await conn.ws.close()


async def cmd_unexpose(args):
    """Handle unexpose command."""
    conn = await connect()
    try:
        success = await expose_entities(conn, args.entities, should_expose=False)
        if success:
            print(f"Successfully unexposed {len(args.entities)} entity(ies) from conversation agent:")
            for entity_id in args.entities:
                print(f"  - {entity_id}")
        else:
            print("ERROR: Failed to unexpose entities")
            sys.exit(1)
    finally:
        await conn.ws.close()


async def cmd_list(args):
    """Handle list command."""
    conn = await connect()
    try:
        exposed = await get_exposed_entities(conn)
        if not exposed:
            print("No entities are exposed to the conversation agent.")
            return

        print(f"Entities exposed to conversation agent ({len(exposed)}):\n")

        # Group by domain
        by_domain = {}
        for entity_id, info in exposed.items():
            domain = entity_id.split(".")[0]
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append((entity_id, info))

        for domain in sorted(by_domain.keys()):
            print(f"{domain}:")
            for entity_id, info in sorted(by_domain[domain]):
                name = info.get("name", "")
                area = info.get("area_id", "")
                suffix = f" ({name})" if name else ""
                suffix += f" [{area}]" if area else ""
                print(f"  {entity_id}{suffix}")
            print()
    finally:
        await conn.ws.close()


async def cmd_check(args):
    """Handle check command."""
    conn = await connect()
    try:
        status = await check_entities(conn, args.entities)
        print("Entity exposure status:\n")
        for entity_id, info in status.items():
            if not info["exists"]:
                print(f"  {entity_id}: NOT FOUND")
            elif info["exposed"]:
                name = info.get("name", "")
                suffix = f" ({name})" if name else ""
                print(f"  {entity_id}: EXPOSED{suffix}")
            else:
                print(f"  {entity_id}: not exposed")
    finally:
        await conn.ws.close()


def main():
    parser = argparse.ArgumentParser(
        description="Manage entity exposure to Home Assistant conversation agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # expose command
    expose_parser = subparsers.add_parser("expose", help="Expose entities to conversation agent")
    expose_parser.add_argument("entities", nargs="+", help="Entity IDs to expose")

    # unexpose command
    unexpose_parser = subparsers.add_parser("unexpose", help="Unexpose entities from conversation agent")
    unexpose_parser.add_argument("entities", nargs="+", help="Entity IDs to unexpose")

    # list command
    subparsers.add_parser("list", help="List all exposed entities")

    # check command
    check_parser = subparsers.add_parser("check", help="Check if specific entities are exposed")
    check_parser.add_argument("entities", nargs="+", help="Entity IDs to check")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "expose":
        asyncio.run(cmd_expose(args))
    elif args.command == "unexpose":
        asyncio.run(cmd_unexpose(args))
    elif args.command == "list":
        asyncio.run(cmd_list(args))
    elif args.command == "check":
        asyncio.run(cmd_check(args))


if __name__ == "__main__":
    main()
