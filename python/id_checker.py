import asyncio
import moteus
import moteus_pi3hat

async def main():
    # Define the transport without specifying a servo bus map to scan all buses
    transport = moteus_pi3hat.Pi3HatRouter()

    print("Scanning for connected servos...")

    # Create a list to store discovered servo IDs
    discovered_servos = []

    # Iterate over possible servo IDs (moteus typically supports 1 to 127)
    for servo_id in range(1, 128):
        # Create a controller instance for the current ID
        controller = moteus.Controller(id=servo_id, transport=transport)

        try:
            # Attempt to query the servo
            result = await transport.cycle([controller.make_query()])

            # Verify that the response contains a valid POSITION register
            if result and moteus.Register.POSITION in result[0].values:
                discovered_servos.append(servo_id)
                print(f"Found servo with ID: {servo_id}")

        except Exception:
            # Ignore errors for IDs that do not respond
            pass

    # Print the results
    if discovered_servos:
        print(f"Discovered servos: {discovered_servos}")
    else:
        print("No servos found.")

if __name__ == "__main__":
    asyncio.run(main())
