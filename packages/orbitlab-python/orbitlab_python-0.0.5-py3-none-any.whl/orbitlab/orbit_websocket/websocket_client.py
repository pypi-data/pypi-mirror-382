import socket
import json
import time
import threading
import uuid
import sys
from orbitlab.orbit_utils.face_ids import FaceId

def auto_stop_on_error(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception:
            self.stop()
            raise  # re-raise so you still see the original error
    return wrapper

class OrbitWebsocketClient(threading.Thread):
    def __init__(self, host = '192.168.31.141', *args, **kwargs):
        super(OrbitWebsocketClient, self).__init__(target=self.__target_with_callback, args=args, kwargs=kwargs)
        self.sub_callbacks = {}
        self.client_callbacks = {}
        self.buffer = ""
        self.host = host
        self.port = 65432
        self.client_id = str(uuid.uuid4())
        self.is_running = False
        self.__waiting_for_service = True
        self.__service_available = False
        self.client = self.__tel_connect()

        self.driver_data = {}
        self.image_data = {}
        self.arduino_data = {}

        self.__start_subscriptions()
        self.start()
        time.sleep(1)
    
    def __start_subscriptions(self):
        print("Starting subscriptions...")
        self.__subscribe("motor_driver_topic", "arduino_msgs/MotorDriver", self.__driver_callback)
        time.sleep(0.1)
        self.__subscribe("arduino_topic", "arduino_msgs/Buttons", self.__arduino_callback)
        time.sleep(0.1)
        self.__subscribe("camera/compressed/image", "sensor_msgs/CompressedImage", self.__camera_callback)

    @auto_stop_on_error
    def set_rpm(self, rpm:list):
        """Set the RPM of the robot's wheels.

        Args:
            rpm (list): A list of two integer values [left_rpm, right_rpm]
        """
        if not isinstance(rpm, list) or len(rpm) != 2 or not all(isinstance(x, (int)) for x in rpm):
            raise ValueError("RPM must be a list of integer two values.")
        if not all(-30 <= x <= 30 for x in rpm):
            raise ValueError("RPM values must be between -30 and 30.")
        self.__publish("cmd_rpm", "std_msgs/Int16MultiArray", json.dumps({"data": rpm}))
    
    def change_face(self, face_id:FaceId):
        """Change the robot's facial expression.

        Args:
            face_id (FaceId): An instance of the FaceId enum representing the desired facial expression
        """
        self.__call_service("change_face", "orbit_command_msgs/Face", json.dumps({"face": face_id.value}), None)

    @auto_stop_on_error
    def text_to_speech(self, text:str, block:bool = True):
        """Send a text to the robot to speak.
        
        Args:
            text (str): The text to be spoken by the robot.
            block (bool): If True, wait for the service to complete before returning.
        """
        self.__waiting_for_service = block
        if not isinstance(text, str):
            raise ValueError("Text must be a string.")
        self.__call_service("record_task", "orbit_command_msgs/Records", json.dumps({"records": text}), None)
    
    @auto_stop_on_error
    def play_song(self, song_name:str):
        """Play a predefined song on the robot.

        Args:
            song_name (str): The name of the song to be played.
        """
        if not isinstance(song_name, str):
            raise ValueError("Song name must be a string.")
        print("play song comming soon...")
        self.__call_service('play_music', 'orbit_command_msgs/SetString', json.dumps({"req": song_name}), None)
    
    def dance(self, song_name:str):
        """Make the robot dance to a predefined song.

        Args:
            song_name (str): The name of the song to dance to.
        """
        if not isinstance(song_name, str):
            raise ValueError("Song name must be a string.")
        self.__call_service('dance', "orbit_command_msgs/SetString", json.dumps({"req": song_name}), None)

    @auto_stop_on_error
    def set_rgb(self, rgb:list):
        """Set the RGB color of the robot's LED.

        Args:
            rgb (list): A list of three integer values representing the RGB color [R, G, B].
        """
        if not isinstance(rgb, list) or len(rgb) != 3 or not all(isinstance(x, int) for x in rgb):
            raise ValueError("RGB must be a list of three integer values.")
        if not all(0 <= x <= 255 for x in rgb):
            raise ValueError("RGB values must be between 0 and 255.")
        self.__call_service("arduino_write_value", "arduino_msgs/ArduinoWrite", json.dumps({"cmd_type": 1, "arguments": [6] + rgb}), None)
    
    @auto_stop_on_error
    def set_led_animation(self, animation_type:int, rgb:list):
        """Set the LED animation on the robot.
        
        Args:
            animation_type (int): The type of LED animation (0-5).
            rgb (list): A list of three integer values representing the RGB color [R, G, B].
        """
        if not isinstance(rgb, list) or len(rgb) != 3 or not all(isinstance(x, int) for x in rgb):
            raise ValueError("RGB must be a list of three integer values.")
        if not all(0 <= x <= 255 for x in rgb):
            raise ValueError("RGB values must be between 0 and 255.")
        self.__call_service("arduino_write_value", "arduino_msgs/ArduinoWrite", json.dumps({"cmd_type": 1, "arguments": [animation_type] + rgb}), None)
    
    @auto_stop_on_error
    def set_head_pose(self, x:int, y:int):
        """Set the head pose of the robot.
        
        Args:
            x (int): The horizontal angle in degrees (-300 to 300).
            y (int): The vertical angle in degrees (-300 to 300).
        """
        pose = [x, y]
        if not all(isinstance(x, (int, int)) for x in pose):
            raise ValueError("x and y must be integers.")
        if not all(-300 <= x <= 300 for x in pose):
            raise ValueError("x and y must be between -300 and 300 degrees.")
        self.__call_service("arduino_write_value", "arduino_msgs/ArduinoWrite", json.dumps({"cmd_type": 2, "arguments": pose + [0, 0]}), None)
    
    def head_calibration(self):
        """Calibrate the head position of the robot."""
        self.__call_service("arduino_write_value", "arduino_msgs/ArduinoWrite", json.dumps({"cmd_type": 3, "arguments": [0, 0, 0, 0]}), None)
    
    @auto_stop_on_error
    def turn_left(self, angle: int):
        """Turn the robot left by a specified angle.

        Args:
            angle (float): The angle in degrees to turn left.
        """
        if not isinstance(angle, (int, float)) or not (0 < angle <= 360):
            raise ValueError("Angle must be an int or float between 1 and 360 degrees.")
        self.__call_action("control_motor", "orbit_command_msgs/WheelGoal", json.dumps({"function_id": 2, "goal":float(angle)}), None)
    
    @auto_stop_on_error
    def turn_right(self, angle: int):
        """Turn the robot right by a specified angle.

        Args:
            angle (float): The angle in degrees to turn right.
        """
        if not isinstance(angle, (int, float)) or not (0 < angle <= 360):
            raise ValueError("Angle must be an int or float between 1 and 360 degrees.")
        self.__call_action("control_motor", "orbit_command_msgs/WheelGoal", json.dumps({"function_id": 3, "goal":float(angle)}), None)
    
    @auto_stop_on_error
    def move_forward(self, distance: float):
        """Move the robot forward by a specified distance.

        Args:
            distance (float): The distance in meters to move forward.
        """
        if not isinstance(distance, (int, float)) or not (0 < distance <= 2):
            raise ValueError("Distance must be an int or float between 0 and 2 meters.")
        self.__call_action("control_motor", "orbit_command_msgs/WheelGoal", json.dumps({"function_id": 0, "goal":float(distance)}), None)
    
    @auto_stop_on_error
    def move_backward(self, distance: float):
        """Move the robot backward by a specified distance.

        Args:
            distance (float): The distance in meters to move backward.
        """
        if not isinstance(distance, (int, float)) or not (0 < distance <= 2):
            raise ValueError("Distance must be an int, float between 0 and 2 meters.")
        self.__call_action("control_motor", "orbit_command_msgs/WheelGoal", json.dumps({"function_id": 1, "goal":float(distance)}), None)


    def __target_with_callback(self):
        while self.is_running:
            try:
                data = self.client.recv(1024).decode()
                if not data:
                    print("No data received, stopping client.")
                    self.stop()
                    break
                self.buffer += data

                if "<END>" in self.buffer:
                    messages = self.buffer.split("<END>")
                    self.buffer = messages[-1]
                    msg = messages[0]
                    # print(f"Received size of message: {sys.getsizeof(msg)} bytes")
                    # print(f"Received message: {msg}")
                    msg_obj = json.loads(msg)
                    if msg_obj.get("client_id") != self.client_id:
                        topic = msg_obj.get("topic")
                        msg_type = msg_obj.get("type")

                        if msg_type == "sub":
                            if topic in self.sub_callbacks:
                                self.callback = self.sub_callbacks[topic]
                                self.callback(msg_obj["msg_data"])
                            else:
                                print(f"No callback found for topic: {topic}")
                                continue
                        elif msg_type == "srv" or msg_type == "action":
                            print(f"Received message: {msg}")
                            self.__waiting_for_service = False
                            self.__service_available = msg_obj.get("status", False)
                            if topic in self.client_callbacks and self.__service_available:
                                self.callback = self.client_callbacks[topic]
                                self.callback(msg_obj["msg_data"])
                            else:
                                print(f"No callback found for service topic: {topic}")
                                continue
            
            except Exception as e:
                print(f"Stopping client due to an error. {e}")
                self.stop()
                break
    
    # @auto_stop_on_error
    def __tel_connect(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            print(f'Connected to server {self.host}:{self.port}')
            self.is_running = True
            return s
        except Exception as e:
            raise ConnectionError(f"Failed to connect to server {self.host}:{self.port}. Error: {e}")
    
    def stop(self):
        """Stop the client and close the connection."""
        self.set_rpm([0, 0])  # Stop the robot
        self.is_running = False
        if self.client is not None:
            self.client.close()
    
    def __publish(self, topic, msg_type, msg_data):
        msg_obj = {
            "client_id": self.client_id,
            "type": "pub",
            "topic": topic,
            "msg_type": msg_type,
            "msg_data": msg_data
        }

        self.__send_message(json.dumps(msg_obj))
    
    def __subscribe(self, topic, msg_type, callback=None):
        msg_obj = {
            "client_id": self.client_id,
            "type": "sub",
            "topic": topic,
            "msg_type": msg_type
        }
        if callback is not None:
            self.sub_callbacks[topic] = callback
        self.__send_message(json.dumps(msg_obj))
        print(f"Subscribed to topic: {topic} with type: {msg_type}")
    
    def __call_service(self, topic, msg_type, msg_data, callback=None):
        self.__waiting_for_service = True
        msg_obj = {
            "client_id": self.client_id,
            "type": "serv",
            "topic": topic,
            "msg_type": msg_type,
            "msg_data": msg_data
        }
        if callback is not None:
            self.client_callbacks[topic] = callback
        self.__send_message(json.dumps(msg_obj))
        while self.__waiting_for_service:
            ...
        if not self.__service_available:
            print(f"Service {topic} is not available.")
            # self.start_subscriptions()
            return
        # self.start_subscriptions()
    
    def __call_action(self, topic, msg_type, msg_data, callback=None):
        self.__waiting_for_service = True
        msg_obj = {
            "client_id": self.client_id,
            "type": "action",
            "topic": topic,
            "msg_type": msg_type,
            "msg_data": msg_data
        }
        if callback is not None:
            self.client_callbacks[topic] = callback
        self.__send_message(json.dumps(msg_obj))
        while self.__waiting_for_service:
            ...
        if not self.__service_available:
            print(f"Action {topic} is not available.")
            # self.start_subscriptions()
            return
        print("Action response received.")
        # self.start_subscriptions()
    
    def __send_message(self, msg):
        # print(f'Sending message: {msg}')
        msg = msg + "<END>"
        if self.is_running:
            self.client.sendall(msg.encode())
    
    def __driver_callback(self, msg_data):
        # print(f"Driver callback received message: {type(msg_data)}")
        self.driver_data = msg_data
    
    def __camera_callback(self, msg_data):
        self.image_data = msg_data
        # print(f"Camera callback received message: {(msg_data)}")
    
    def __arduino_callback(self, msg_data):
        self.arduino_data = msg_data

if __name__ == '__main__':
    soc_client = OrbitWebsocketClient()
    # soc_client.set_rpm([30, -30])
    time.sleep(4)
    soc_client.change_face(FaceId.ERROR)
    soc_client.stop()
    