import mido
from mido import Message

class MIDIAppLogic:
    def __init__(self, port_name):
        self.outport = mido.open_output(port_name)
        self.current_octave = 4  # Start at middle octave (C4)
        self.active_notes = {}    # Tracks {note_number: hand_side}
        self.is_sharp_mode = False
        
        # Base MIDI values for the 7 keys (C, D, E, F, G, A, B)
        # These are relative offsets from the start of an octave
        self.note_offsets = [0, 2, 4, 5, 7, 9, 11]

    def process_frame(self, left_mask, right_mask, pinky_y_delta):
        """
        Processes bitmasks: 
        Left fingers (1-4): C, D, E, F
        Right fingers (1-3): G, A, B
        Right Thumb (0): Sharp Toggle
        Right Pinky (4): Octave Scroll (via delta)
        """
        
        # 1. Update State Modifiers
        # Check Right Thumb (Bit 0 of Right Hand) for Sharp mode
        self.is_sharp_mode = bool(right_mask & (1 << 0))
        
        # 2. Handle Octave Scrolling (Right Pinky Delta)
        if abs(pinky_y_delta) > 0.05: # Sensitivity threshold
            if pinky_y_delta < 0: # Moving up on screen
                self.current_octave = min(8, self.current_octave + 1)
            else:
                self.current_octave = max(1, self.current_octave - 1)

        # 3. Map Fingers to Notes
        # We create a list of 'desired' notes based on current finger positions
        target_notes = set()
        
        # Map Left Index, Middle, Ring, Pinky -> C, D, E, F
        for i in range(1, 5): 
            if left_mask & (1 << i):
                target_notes.add(self._calculate_note(i - 1))
        
        # Map Right Index, Middle, Ring -> G, A, B
        for i in range(1, 4):
            if right_mask & (1 << i):
                target_notes.add(self._calculate_note(i + 3))

        # 4. Synchronize MIDI State (Prevent double-triggering)
        self._sync_midi(target_notes)

    def _calculate_note(self, scale_index):
        """Calculates exact MIDI note with Octave and Sharp modifiers"""
        base = (self.current_octave + 1) * 12
        note = base + self.note_offsets[scale_index]
        if self.is_sharp_mode:
            note += 1
        return note

    def _sync_midi(self, target_notes):
        """Standard State Management: Stop notes that left, start notes that arrived"""
        # Stop notes that are no longer pressed
        for note in list(self.active_notes.keys()):
            if note not in target_notes:
                self.outport.send(Message('note_off', note=note, velocity=0))
                del self.active_notes[note]

        # Start new notes
        for note in target_notes:
            if note not in self.active_notes:
                self.outport.send(Message('note_on', note=note, velocity=64))
                self.active_notes[note] = True