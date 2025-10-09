# Audio-Image-Converter

Converts audio to and from a picture representing the frequency-time domain, remaining perceptually lossless. When converting to `.webp`, achieves slightly better compression ratio than an equivalent `.flac`. (Note that this format is not intended to compete with preeexisting audio formats/codecs, and is mostly designed as a novelty, enabling users to visually see the contents of audio files. Slight albeit unnoticeable quality loss is often unavoidable due to the conversions between several data types and representations.)

The image's aspect ratio approximately corresponds to the audio's duration in minutes (with each 1588x1588 square representing 1 minute of audio), and its pixel data represents the fourier transform of the audio, with X axis representing time (left/right channels interleaved), Y axis representing frequency (default nyquist at 21000Hz), hue representing phase, and amplitude being represented as a floating-point number, where lightness is the exponent and saturation the fraction. There is slight redundancy between lightness and saturation to accomodate for the more sparse regimes of the HSL colourspace's domain.

## Usage
```
usage: soundcrystal [-h] [-V] [-sr [SAMPLE_RATE]] [-f [FORMAT]] input [output]

Bidirectional spectrogram-based audio-image converter

positional arguments:
  input                 Input filename
  output                Output filename

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -sr, --sample_rate [SAMPLE_RATE]
                        Sample rate; defaults to 42000
  -f, --format [FORMAT]
                        Output format; defaults to opus or webp depending on input
```