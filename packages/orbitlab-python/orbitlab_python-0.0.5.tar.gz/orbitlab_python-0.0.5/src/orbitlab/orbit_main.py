from .orbit_websocket.websocket_client import OrbitWebsocketClient
import base64
import numpy as np
import cv2
import datetime

class Orbit(OrbitWebsocketClient):
    """Initialize the Orbit robot client.
    
    Args:
        host (str): The IP address of the Orbit robot.
    """
    def __init__(self, host: str):
        super().__init__(host=host)

        self.RADIUS = 0.1
        self.WHEEL_L = 0.5
        
    def voltage(self) -> float:
        """Get the voltage of the robot.
        
        Returns: 
            voltage: Voltage in volts (V).
        """
        return round(self.driver_data.get("motor_voltage", 0.0), 2)
    
    def encoder(self) -> list:
        """Get the encoder values of the robot.

        Returns:
            encoder: A list of two encoder values [left_encoder, right_encoder].
        """
        return self.driver_data.get("encoder", [0, 0])
    
    def speed(self) -> list:
        """Get the speed of the robot. Returns a list of two speed values.
        
        Returns:
            speed: A list of two speed values [left_speed, right_speed] in revolution per minute (RPM).
        """
        return self.driver_data.get("speed", [0.0, 0.0])
    
    def current(self) -> float:
        """Get the current of the robot.
        
        Returns:
            current: Current in amperes (A).
        """
        return round(self.arduino_data.get("current", 0.0), 2)
    
    def temperature(self) -> float:
        """Get the temperature of the robot.
        
        Returns:
            temperature: Temperature in degrees Celsius (°C).
        """
        return round(self.arduino_data.get("temp", 0.0), 2)
    
    def distance_value(self) -> float:
        """Get the distance traveled by the robot.
        
        Returns:
            distance: Distance in meters (m).
        """
        return round(self.arduino_data.get("distance", 0.0), 2)
    
    def ldr_value(self) -> int:
        """Get the light-dependent resistor (LDR) value of the robot.
        
        Returns:
            ldr: LDR value as an integer.
        """
        return int(self.arduino_data.get("ldr", 0))
    
    def save_image(self):
        """Save the current image from the robot's camera."""
        if self.image_data:
            epox = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            compression_format = self.image_data.get("format", "")
            data = self.image_data.get("data", "").encode('utf-8')
            image_bytes = base64.b64decode(data) if data else b''
            print(f"Saving image with epox: {epox}, format: {compression_format}, data length: {len(data)}")
            if compression_format and data:
                filename = f"orbit_image_{epox}.{compression_format}"
                with open(filename, 'wb') as file:
                    file.write(image_bytes)
                print(f"Image saved as {filename}")
            else:
                print("Image data is incomplete.")
    
    def capture_image(self) -> np.ndarray:
        """Capture the current image from the robot's camera 
        
        Returns:
            image: The captured image as a cv2 Mat object, or None if no image data is available.
        """
        if self.image_data:
            data = self.image_data.get("data", "")
            if data and isinstance(data, str):
                image_bytes = base64.b64decode(data.encode('utf-8'))
                np_array = np.frombuffer(image_bytes, dtype=np.uint8)
                image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
                return image
        
        else:
            print("No image data available.")
            return None