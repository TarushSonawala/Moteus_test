import asyncio
import time
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
        return

    print("\nReading position data and data rate...")

    # Create controllers for discovered servos
    servos = {
        servo_id: moteus.Controller(id=servo_id, transport=transport)
        for servo_id in discovered_servos
    }

    # Continuously read position data and calculate data rate
    try:
        while True:
            start_time = time.time()
            commands = [servo.make_query() for servo in servos.values()]
            results = await transport.cycle(commands)
            elapsed_time = time.time() - start_time

            # Print position data and data rate
            for result in results:
                servo_id = result.arbitration_id
                position = result.values.get(moteus.Register.POSITION, "N/A")
                print(f"Servo ID: {servo_id}, Position: {position:.6f} radians")

            # Calculate data rate in Hz (cycles per second)
            data_rate_hz = 1 / elapsed_time if elapsed_time > 0 else 0
            print(f"Data Rate: {data_rate_hz:.2f} Hz\n")

            await asyncio.sleep(0.02)  # 20ms delay between cycles

    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    asyncio.run(main())
