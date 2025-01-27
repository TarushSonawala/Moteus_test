import asyncio
import moteus
import moteus_pi3hat

async def main():
    # Explicitly map servo IDs to buses
    servo_bus_map = {
        1: [11, 12],  # Bus 1 (JC1) -> IDs 11, 12
        2: [21, 22],  # Bus 2 (JC2) -> IDs 21, 22
    }

    # Initialize Pi3HatRouter
    transport = moteus_pi3hat.Pi3HatRouter(servo_bus_map=servo_bus_map)

    print("Scanning for connected servos on Bus 1 (JC1) and Bus 2 (JC2)...")

    discovered_servos = {1: [], 2: []}

    # Iterate over buses and their expected servo IDs
    for bus, ids in servo_bus_map.items():
        print(f"\nScanning bus {bus}...")
        for servo_id in ids:
            controller = moteus.Controller(id=servo_id, transport=transport)
            try:
                # Query the servo
                result = await transport.cycle([controller.make_query()])
                print(f"Raw result from bus {bus}, ID {servo_id}: {result}")
                for res in result:
                    if res.arbitration_id == servo_id:
                        discovered_servos[bus].append(servo_id)
                        print(f"Found servo with ID: {servo_id} on bus {bus}")
            except Exception as e:
                print(f"Error querying servo ID {servo_id} on bus {bus}: {e}")

    # Print results
    print("\nScan Results:")
    for bus, ids in discovered_servos.items():
        if ids:
            print(f"Discovered servos on bus {bus}: {ids}")
        else:
            print(f"No servos found on bus {bus}")

if __name__ == "__main__":
    asyncio.run(main())
