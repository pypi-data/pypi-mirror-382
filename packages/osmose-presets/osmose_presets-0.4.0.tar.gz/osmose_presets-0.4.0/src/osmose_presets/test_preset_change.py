import mido
import time


def send_preset_change(port: str, cc: int, pgm: int):
   print("Attempting to open port:", port)
   print("Available input ports:", mido.get_input_names())

   try:
      output = mido.open_output(port)
   except OSError as e:
      print(f"Error opening MIDI port '{port}': {e}")
      return False

   cc_msg = mido.Message("control_change", channel=0, control=0, value=cc)
   print(f"Sending CC message: {cc_msg.hex()}")
   output.send(cc_msg)

   time.sleep(0.4)

   pgm_msg = mido.Message("program_change", channel=0, program=pgm)
   print(f"Sending PGM message: {pgm_msg.hex()}")
   output.send(pgm_msg)

   output.close()


send_preset_change("MIDIIN2 (Osmose) 1", 32, 92)
