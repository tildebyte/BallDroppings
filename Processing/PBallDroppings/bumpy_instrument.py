from ddf.minim.ugens import Oscil, WavetableGenerator
from ddf.minim.ugens import Instrument, Waves, Frequency
# This Instrument definition was lifted directly from the
#     Synthesis:oscilEnvExample example in the Minim documentation.


class BumpyInstrument(Instrument):

    def __init__(self, pitch, amplitude, out):
        self.out = out
        freq = Frequency.ofMidiNote(pitch)
        # The name of the method "gen7" is a reference to a genorator in Csound.
        # This is a somewhat silly, but demonstrative wave. It rises from 0 to 1
        # over 1/8th of the time, then goes to 0.25 over 1/8th of it's time, then
        # drops to 0.15 over 1/128th of it's time, and then decays to 0
        # for the rest of the time.
        # Note that this envelope is of fixed shape regardless of duration.
        myEnv = WavetableGenerator.gen7(8192,
                                        [0.00, 1.00, 0.25, 0.15, 0.00],
                                        [1024, 1024, 64, 6080])

        # Create instances of any UGen objects as necessary.
        # The tone is the first ten harmonics of a saw wave.
        self.toneOsc = Oscil(freq, 1.0, Waves.sawh(10))
        self.envOsc = Oscil(1.0, amplitude, myEnv)
        # Patch everything up to the output.
        self.envOsc.patch(self.toneOsc.amplitude)

    # Every Instrument must have a noteOn(float) method.
    def noteOn(self, dur):
        # The duration of the amplitude envelope is set to the length
        # of the note.
        self.envOsc.setFrequency(1.0 / dur)
        # The tone oscillator is patched directly to the output.
        self.toneOsc.patch(self.out)

    # Every Instrument must have a noteOff() method.
    def noteOff(self):
        # Unpatch the tone oscillator when the note is over.
        self.toneOsc.unpatch(self.out)
