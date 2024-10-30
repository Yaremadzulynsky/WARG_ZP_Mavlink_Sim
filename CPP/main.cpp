#include <mavlink.h>
#include <thread>
#include <chrono>
#include <iostream>
#include <cstring>
#include <arpa/inet.h>

// Define the UDP port to send data to (e.g., 14550)
constexpr int TARGET_PORT = 14550;
constexpr char TARGET_IP[] = "127.0.0.1";

// UDP socket setup
int udp_socket;
sockaddr_in target_address;

// Function to send MAVLink packets over UDP
void send_mavlink_packet(const mavlink_message_t& msg) {
    uint8_t buffer[2048];
    int length = mavlink_msg_to_send_buffer(buffer, &msg);
    sendto(udp_socket, buffer, length, 0, (sockaddr*)&target_address, sizeof(target_address));
}

// Function to send a MAVLink heartbeat
void send_heartbeat() {
    std::cout << "Sending heartbeat" << std::endl;
    mavlink_message_t msg;
    mavlink_msg_heartbeat_pack(1, 200, &msg, MAV_TYPE_QUADROTOR, MAV_AUTOPILOT_ARDUPILOTMEGA, 0, 0, MAV_STATE_ACTIVE);
    send_mavlink_packet(msg);
}

// Function to send system status
void send_sys_status() {
    mavlink_message_t msg;
    mavlink_msg_sys_status_pack(1, 200, &msg, 0b111111111111111111111111, 0b111111111111111111111111, 0b111111111111111111111111, 500, 12000, -1, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    send_mavlink_packet(msg);
}

// Function to send global position
void send_global_position_int(int32_t lat, int32_t lon) {
    mavlink_message_t msg;
    mavlink_msg_global_position_int_pack(1, 200, &msg, 0, lat, lon, 0, 0, 0, 0, 0, 0);
    send_mavlink_packet(msg);
}

// Function to receive MAVLink messages (stub, as handling incoming packets in C++ requires more setup)
void receive_mavlink_messages() {
    uint8_t buffer[2048];
    mavlink_message_t msg;
    mavlink_status_t status;

    while (true) {
        ssize_t recv_len = recvfrom(udp_socket, buffer, sizeof(buffer), 0, nullptr, nullptr);
        if (recv_len > 0) {
            for (ssize_t i = 0; i < recv_len; ++i) {
                if (mavlink_parse_char(MAVLINK_COMM_0, buffer[i], &msg, &status)) {
                    std::cout << "Received message: " << mavlink_msg_to_send_buffer(buffer, &msg) << std::endl;
                }
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

// Function to send MAVLink messages
void send_mavlink_messages() {
    int32_t lat = 473000000;  // 47.3000000 degrees
    int32_t lon = 85700000;   // 8.5700000 degrees

    while (true) {
        send_heartbeat();
        send_global_position_int(lat, lon);
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
}

int main() {
    // Initialize UDP socket
    udp_socket = socket(AF_INET, SOCK_DGRAM, 0);
    if (udp_socket < 0) {
        std::cerr << "Failed to create UDP socket" << std::endl;
        return -1;
    }

    std::memset(&target_address, 0, sizeof(target_address));
    target_address.sin_family = AF_INET;
    target_address.sin_port = htons(TARGET_PORT);
    inet_pton(AF_INET, TARGET_IP, &target_address.sin_addr);

    // Send system status
    send_sys_status();
    std::cout << "System status sent" << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(1));

    // Start receiver and sender threads
    std::thread receiver_thread(receive_mavlink_messages);
    receiver_thread.detach();
    std::thread sender_thread(send_mavlink_messages);
    sender_thread.detach();

    // Keep the main thread running
    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    return 0;
}