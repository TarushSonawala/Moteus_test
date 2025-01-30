#include <inttypes.h>
#include <stdio.h>

#include <algorithm>
#include <vector>
#include <iostream>

#include "mjbots/moteus/moteus.h"
#include "mjbots/moteus/pi3hat_moteus_transport.h"

namespace {
using namespace mjbots;

// A simple way to get the current time accurately as a double.
static double GetNow() {
  struct timespec ts = {};
  ::clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
  return static_cast<double>(ts.tv_sec) +
      static_cast<double>(ts.tv_nsec) / 1e9;
}

void DisplayUsage() {
  std::cout << "Usage: read_positions\n";
  std::cout << "\n";
  std::cout << "  This program queries and displays the position data of 14 servos:\n";
  std::cout << "   - IDs 11 to 17 on bus 1\n";
  std::cout << "   - IDs 21 to 27 on bus 2\n";
}
}

int main(int argc, char** argv) {
  if (argc > 1 && (std::string(argv[1]) == "-h" || std::string(argv[1]) == "--help")) {
    DisplayUsage();
    std::exit(0);
  }

  // Register the Pi3Hat transport
  mjbots::pi3hat::Pi3HatMoteusFactory::Register();

  // List of servo IDs and corresponding buses
  struct ServoInfo {
    int id;
    int bus;
  };

  std::vector<ServoInfo> servos;
  for (int id = 11; id <= 17; ++id) {  // Bus 1, IDs 11-17
    servos.push_back({id, 1});
  }
  for (int id = 21; id <= 27; ++id) {  // Bus 2, IDs 21-27
    servos.push_back({id, 2});
  }

  // Initialize controllers for all servos
  std::vector<moteus::Controller> controllers;
  for (const auto& servo : servos) {
    controllers.emplace_back([&]() {
      moteus::Controller::Options options;
      options.id = servo.id;
      options.bus = servo.bus;
      options.query_format.position = moteus::kInt16;
      // options.query_format.velocity = moteus::kInt16;
      // options.query_format.torque = moteus::kIgnore;
      return options;
    }());
  }

  constexpr double kStatusPeriod = 0.1;

  uint64_t cycles = 0;
  auto next_status = GetNow() + kStatusPeriod;
  uint64_t hz_count = 0;

  int rx_timeout = 0;

  // Store the latest query results for all servos
  std::vector<moteus::Query::Result> query_results(servos.size());

  while (true) {
    cycles++;
    hz_count++;

    // Query each servo and store results
    for (size_t i = 0; i < controllers.size(); ++i) {
      auto maybe_servo_state = controllers[i].SetQuery();
      if (!!maybe_servo_state) {
        query_results[i] = maybe_servo_state->values;
      } else {
        rx_timeout++;
      }
    }

    // Remove sleep to maximize Hz

    // Print status at regular intervals
    const auto now = GetNow();
    if (now > next_status) {
      printf("%.3f %6" PRIu64 " %6.1fHz\n", now, cycles, hz_count / kStatusPeriod);

      // Print positions for all servos
      for (size_t i = 0; i < servos.size(); ++i) {
        const auto& servo = servos[i];
        const auto& result = query_results[i];
        printf("  Servo %d (Bus %d): Mode %d, Position %.3f\n",
               servo.id, servo.bus, static_cast<int>(result.mode), result.position);
      }

      printf("RX Timeouts: %d\n", rx_timeout);
      fflush(stdout);

      hz_count = 0;
      next_status += kStatusPeriod;
    }
  }

  return 0;
}
