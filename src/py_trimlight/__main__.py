import asyncio
import logging

from py_trimlight.trimlight_local_client import (
    CATEGORY_BUILTIN,
    CATEGORY_CUSTOM,
    CHANNEL_ORDERS,
    COMBINED_EFFECT_ID,
    IC_TYPES,
    OverlayKind,
    Repeat,
    SwitchState,
    TrimlightLocalClient,
)


async def main():
    async with TrimlightLocalClient("10.4.1.90", reply_timeout=1) as client:
        print("Connected to Trimlight device")
        print_state(client)


def print_state(client: TrimlightLocalClient) -> None:
    state = client.state
    assert state is not None
    mode = (
        SwitchState(state.switch_state).name.lower()
        if state.switch_state in SwitchState._value2member_map_
        else state.switch_state
    )
    print(f"verified:      {client.verified}")
    print(f"switch state:  {mode}")
    print(f"IC type:       {IC_TYPES.get(state.ic_type, state.ic_type)}")
    print(
        f"channel order: {CHANNEL_ORDERS.get(state.channel_order, state.channel_order)}"
    )
    print("ports:         " + ", ".join(f"{start}-{end}" for start, end in state.ports))
    if client.firmware is not None:
        mcu = client.firmware.mcu_version
        print(
            f"firmware:      {client.firmware.version} (module {client.firmware.module_version}, MCU {mcu:#06x})"
            if mcu is not None
            else f"firmware:      {client.firmware.version}"
        )
    print(f"clock:         {state.clock}")
    names = {e.id: e.name for e in state.library} | {
        COMBINED_EFFECT_ID: "Combined effect"
    }
    print(f"saved effects ({len(state.library)}):")
    for effect in state.library:
        kind = (
            "pattern"
            if effect.category == CATEGORY_CUSTOM
            else "built-in"
            if effect.category == CATEGORY_BUILTIN
            else f"category {effect.category}"
        )
        print(
            f"  {effect.id:3d}  {effect.name:25}  {kind:8} mode={effect.mode:3d} speed={effect.speed:3d} brightness={effect.brightness:3d}"
        )
    if state.combined is not None:
        print(
            f"combined effect: {', '.join(names.get(i, str(i)) for i in state.combined.effect_ids)}, {state.combined.interval} min each"
        )
    for overlay in state.overlays:
        print(
            f"overlay:       {OverlayKind(overlay.kind).name.lower() if overlay.kind in OverlayKind._value2member_map_ else overlay.kind} on {names.get(overlay.effect_id, overlay.effect_id)}"
        )
    print(f"calendar schedules ({len(state.calendar)}):")
    for s in state.calendar:
        print(
            f"  {s.id:3d}  {s.start[0]:02d}-{s.start[1]:02d} to {s.end[0]:02d}-{s.end[1]:02d}  {s.on_time:%H:%M}-{s.off_time:%H:%M}  {names.get(s.effect_id, s.effect_id)}"
        )
    for i, d in enumerate(state.daily, 1):
        repeat = (
            Repeat(d.repeat).name.lower().replace("_", " ")
            if d.repeat in Repeat._value2member_map_
            else d.repeat
        )
        print(
            f"daily {i}:       {'on ' if d.enabled else 'off'}  {repeat:10}  {d.on_time:%H:%M}-{d.off_time:%H:%M}  {names.get(d.effect_id, d.effect_id)}"
        )
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        print(f"raw sync data ({len(state.raw)} bytes):")
        for i in range(0, len(state.raw), 32):
            print(f"  {i:04x}  {state.raw[i : i + 32].hex(' ')}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    asyncio.run(main())
