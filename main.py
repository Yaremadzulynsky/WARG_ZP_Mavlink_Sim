from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import time
import queue
import threading
from typing import Callable

# Define the UDP port to send data to (e.g., 14550)
TARGET_PORT = 14550

task_queue = queue.Queue()

data_steam_activation = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
data_steam_frequency =  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ,1]

# Create a UDP connection for sending MAVLink packets
mavlink_connection = mavutil.mavlink_connection(f'udpout:127.0.0.1:{TARGET_PORT}')
mav: common.MAVLink = mavlink_connection.mav
# mavlink_receiver = mavutil.mavlink_connection(f'udpin:127.0.0.1:{TARGET_PORT}')


# Function to send a MAVLink heartbeat
def send_heartbeat():
    mav.heartbeat_send(
        type=mavutil.mavlink.MAV_TYPE_QUADROTOR,  # Adjust to vehicle type
        autopilot=mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
        base_mode=1,
        custom_mode=0,
        system_status=mavutil.mavlink.MAV_STATE_ACTIVE
    )

# Function to send system status
def send_sys_status():
    mav.sys_status_send(
        onboard_control_sensors_present=0b111111111111111111111111,  # Simulate all sensors present
        onboard_control_sensors_enabled=0b111111111111111111111111,  # Simulate all sensors enabled
        onboard_control_sensors_health=0b111111111111111111111111,   # Simulate all sensors healthy
        load=500,            # System load (0-1000)
        voltage_battery=12000,  # Battery voltage in mV
        current_battery=-1,   # Battery current in 10mA (set to -1 if not measured)
        battery_remaining=80,  # Battery remaining in percentage
        drop_rate_comm=0,    # Communication drop rate (% * 100)
        errors_comm=0,       # Communication errors
        errors_count1=0,     # Sensor error count 1
        errors_count2=0,     # Sensor error count 2
        errors_count3=0,     # Sensor error count 3
        errors_count4=0      # Sensor error count 4
    )
    
def send_global_position_int():
    mav.global_position_int_send(
        time_boot_ms=0,
        lat=lat,
        lon=lon,
        alt=0,
        relative_alt=0,
        vx=0,
        vy=0,
        vz=0,
        hdg=0
    )

# Example lat/lon values for simulation
lat = 0  # 47.3000000 degrees
lon = 0   # 8.5700000 degrees


def init_req_stream_id_n(index: int, func: Callable):
    while True:
        if data_steam_activation[index] == 1:
            print(f"Queuing stream id {index}")
            def verbose_func():
                func()
                print(f"Stream id {index} sent")
            task_queue.put(verbose_func)
            time.sleep(1/data_steam_frequency[index])

def init_req_stream_id_6():
    def func():
        mav.local_position_ned_send(time_boot_ms=0,
            x=0,
            y=0,
            z=0,
            vx=0,
            vy=0,
            vz=0)
        mav.global_position_int_send(
            time_boot_ms=0,
            lat=lat,
            lon=lon,
            alt=0,
            relative_alt=0,
            vx=0,
            vy=0,
            vz=0,
            hdg=0)
    init_req_stream_id_n(6, func)
    
def init_req_stream_id_2():
    def func():
        # GPS_STATUS, CONTROL_STATUS, AUX_STATUS
        mav.gps_status_send(
            satellites_visible=10,
            satellite_prn=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            satellite_used=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            satellite_elevation=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            satellite_azimuth=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            satellite_snr=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        
    
            
    init_req_stream_id_n(2, func)



def init_req_stream_heartbeat():
    while True:
        send_heartbeat()
        time.sleep(1)



def receive_mavlink_messages():
    while True:
        msg = mavlink_connection.recv_match(blocking=False)
        if msg is not None:
            if msg.get_type() == 'REQUEST_DATA_STREAM':
                
                data_steam_activation[msg.req_stream_id] = msg.to_dict()['start_stop']
                data_steam_frequency[msg.req_stream_id] = msg.to_dict()['req_message_rate']
                # print(data_steam_activation)
                # print(f"DATA_REQ_IGNORED")
                # print(f"Received message: {msg.to_dict()}")
                continue
            else:
                # print(f"Received message: {msg.to_dict()['mavpackettype']}")
                # print(f"Received message: {msg.to_dict()}")
                continue
        time.sleep(0.1)

def send_mavlink_messages(): 
    req_stream_id_6_thread = threading.Thread(target=init_req_stream_id_6, daemon=True)
    req_stream_id_6_thread.start()
    req_stream_id_2_thread = threading.Thread(target=init_req_stream_id_2, daemon=True)
    req_stream_id_2_thread.start()
    
    
    heartbeat_thread = threading.Thread(target=init_req_stream_heartbeat, daemon=True)
    heartbeat_thread.start()
    
    while True:
        
        # send_global_position_int()
        
        time.sleep(1)


# if __name__ == "__main__":
#     # Send system status
#     send_sys_status()
#     print("System status sent")
#     time.sleep(1)
        
        
#     receiver_thread = threading.Thread(target=receive_mavlink_messages, daemon=True)
#     receiver_thread.start()
#     sender_thread = threading.Thread(target=send_mavlink_messages, daemon=True)
#     sender_thread.start()
    
#     while True:
#         time.sleep(1)


# Create a thread-safe queue
# outbound_queue = queue.Queue()

# def message_producer():
#     """Simulates a thread that adds messages to the queue."""
#     for i in range(5):
#         message = f"Message {i}"
#         outbound_queue.put(message)
#         print(f"Produced: {message}")
#         time.sleep(1)  # Simulate message production delay

def main():
    receiver_thread = threading.Thread(target=receive_mavlink_messages, daemon=True)
    receiver_thread.start()
    sender_thread = threading.Thread(target=send_mavlink_messages, daemon=True)
    sender_thread.start()
    while True:
        while not task_queue.empty():
            try:
                task = task_queue.get(timeout=1)  # Get a function from the queue
                task()  # Execute the function
                
                task_queue.task_done()  # Mark the task as done
            except queue.Empty:
                pass  # If the queue is empty, wait for new tasks
            
            # fastest_loop_rate = max(data_steam_frequency)
            time.sleep(1/(max(data_steam_frequency)+1))

if __name__ == "__main__":
    main()