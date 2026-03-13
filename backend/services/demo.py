"""Demo agents system - generates simulated field activity."""
import asyncio
import logging
import random as _random
from datetime import datetime, timezone, timedelta
from database import db
from constants import DEMO_COUNTRIES, DEMO_ALIASES, DIRECTIONS

logger = logging.getLogger(__name__)

def _build_demo_agents():
    agents = []
    for i in range(50):
        country, code = DEMO_COUNTRIES[i % len(DEMO_COUNTRIES)]
        agents.append({
            "agent_id": f"demo-agent-{i:03d}",
            "alias": DEMO_ALIASES[i],
            "country": country,
            "country_code": code,
            "orientation_direction": DIRECTIONS[i % 4]
        })
    return agents


DEMO_AGENTS = _build_demo_agents()


async def _seed_demo_agents():
    """Seed demo agents into DB if not present."""
    existing = await db.demo_agents.count_documents({})
    if existing == 0:
        await db.demo_agents.insert_many([{**a} for a in DEMO_AGENTS])
        logger.info(f"Seeded {len(DEMO_AGENTS)} demo agents")


async def _generate_demo_events():
    """Generate a batch of demo activity events."""
    now = datetime.now(timezone.utc)
    # Pick 8-15 random agents to act
    batch_size = _random.randint(8, 15)
    acting = _random.sample(DEMO_AGENTS, min(batch_size, len(DEMO_AGENTS)))

    events = []
    for agent in acting:
        # 70% chance to use their primary direction, 30% random
        if _random.random() < 0.7:
            direction = agent["orientation_direction"]
        else:
            direction = _random.choice(DIRECTIONS)

        # Spread timestamps over the last 5 minutes
        offset_seconds = _random.randint(0, 290)
        ts = (now - timedelta(seconds=offset_seconds)).isoformat()

        events.append({
            "agent_id": agent["agent_id"],
            "alias": agent["alias"],
            "country": agent["country"],
            "country_code": agent["country_code"],
            "direction": direction,
            "timestamp": ts,
            "demo": True,
            "type": "demo_action"
        })

    if events:
        await db.demo_events.insert_many(events)
        # Clean events older than 3 hours
        cutoff = (now - timedelta(hours=3)).isoformat()
        await db.demo_events.delete_many({"timestamp": {"$lt": cutoff}})

    logger.info(f"Generated {len(events)} demo events")


async def _demo_event_loop():
    """Background loop: generate demo events every 5 minutes."""
    await asyncio.sleep(5)  # Wait for DB to be ready
    await _seed_demo_agents()
    # Generate an initial batch immediately
    await _generate_demo_events()
    while True:
        await asyncio.sleep(300)  # 5 minutes
        try:
            await _generate_demo_events()
        except Exception as e:
            logger.error(f"Demo event generation error: {str(e)}")
