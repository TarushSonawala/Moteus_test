import asyncio
import moteus
import moteus_pi3hat

async def main():
    # Define the transport with the servo bus map
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={
            1: [11],
            2: [12],
            3: [13],
            4: [14],
        },
    )

    # Create one 'moteus.Controller' instance for each servo
    servos = {
        servo_id: moteus.Controller(id=servo_id, transport=transport)
        for servo_id in [11, 12, 13, 14]
    }

    # Send a 'stop' command to all servos to clear any faults
    await transport.cycle([x.make_stop() for x in servos.values()])

    while True:
        # Create query commands to request servo positions
        commands = [
            servos[servo_id].make_query() for servo_id in [11, 12, 13, 14]
        ]

        # Send the commands and receive results
        results = await transport.cycle(commands)

        # Print the position of each servo for which a response was received
        print(
            ", ".join(
                f"(ID: {result.arbitration_id}, Position: {result.values.get(moteus.Register.POSITION, 'N/A')})"
                for result in results
            )
        )

        # Wait 20ms between cycles to avoid overwhelming the system
        await asyncio.sleep(0.02)

if __name__ == "__main__":
    asyncio.run(main())
