import json
from kafka import KafkaConsumer
from logic_engine import MIDIAppLogic # Ensure this file is in the same folder

# 1. Initialize logic (Find your port name in Step 2 below)
# On Mac, "IAC Driver Bus 1" is the standard virtual port
synth = MIDIAppLogic(port_name="IAC Driver Bus 2") 

consumer = KafkaConsumer(
    'gestures_raw',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("--- MIDI Engine Active & Listening to Kafka ---")

last_pinky_y = None

try:
    for message in consumer:
        data = message.value
        left_mask = data.get("left_mask", 0)
        right_mask = data.get("right_mask", 0)
        current_pinky_y = data.get("pinky_y", 0.0)

        # Calculate delta for the Octave Scroll
        delta_y = 0
        if last_pinky_y is not None:
            delta_y = current_pinky_y - last_pinky_y
        last_pinky_y = current_pinky_y

        # TRIGGER THE SOUND
        synth.process_frame(left_mask, right_mask, delta_y)

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    consumer.close()