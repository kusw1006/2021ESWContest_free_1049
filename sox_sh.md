```shell
################################################################################
# sox cheat sheet
################################################################################
# Example commands for the sox command-line audio processing tool,
# for manipulating or batch processing audio files.
################################################################################
# Daniel Jones <dan@chirp.io>
################################################################################

################################################################################
#### GENERAL USAGE AND HELP
################################################################################

# General usage.
sox [general_flags] [input_flags][infile] [output_flags][outfile] [effects...]

# Get help.
sox

# Deeper commentary on each function and effect.
man sox

# Help on arguments for a particular effect.
sox --help-effect reverb

################################################################################
#### GETTING INFORMATION
################################################################################

# Display general information (samplerate, bit depth, duration, ...)
sox --info input.wav

# Process the audio contents to calculate properties such as RMS.
sox input.wav -n stats

################################################################################
#### CONVERTING BETWEEN FILE FORMATS
################################################################################
# sox automatically infers file type from the extension.

# Convert to 8kHz, 1-channel wav.
sox input.wav -r 8000 -c 1 output.wav

# Convert to mp3.
sox input.wav output.mp3

# Convert to mp3 with specified bitrate in kbps.
sox input.wav -C 256 output.mp3

# Convert from a .raw file of known format to a wav file.
sox -r 44100 -e signed-integer -b 16 chirp-raw-audio.raw chirp-raw-audio.wav

################################################################################
#### SYNTHESIZING AUDIO
################################################################################

# Generate 1 second of white noise.
sox -n output.wav synth 1 noise

# Generate a 1-second sine tone.
sox -n output.wav synth 1 sine 440

# Generate a 10-second sine sweep.
sox -n output.wav synth 10 sine 0:20000

# Exponential sine sweep
sox -n -r 44100 sine-sweep.wav synth 10 sine 5/22050

# Dirac impulse
sox -n -r 44100 impulse.wav synth 1s square pad 0 44099s

################################################################################
#### PLAYING AUDIO
################################################################################

# Play an audio file through the default system audio output.
play input.wav

# Play synthesized audio.
play -n synth sine 440 trim 0 1 gain -12

################################################################################
#### COMBINING AUDIO
################################################################################

# Combine two files by concatenation.
sox a.wav b.wav c.wav concatenated.wav

# Combine two files by mixing their contents.
sox -m a.wav b.wav c.wav mixed.wav

################################################################################
#### MODIFYING AUDIO
################################################################################

# Reduce level by 12dB
sox speech.wav output.wav gain -12

# Crop to the first 1 second of the file.
sox speech.wav output.wav trim 0 1

# Reverse the contents.
sox speech.wav output.wav reverse

# Normalise the contents to 0dBFS.
sox speech.wav output.wav norm

# Equaliser (-6dB @ 100Hz, -24dB @ 8000Hz)
sox speech.wav output.wav bass -6 100 treble -24 8000

# Add room modelling reverb.
sox speech.wav output.wav reverb 50 50 100

# Trim digital silence from start and end.
sox input.wav trimmed/output.wav silence 1 0.1 0 1 0.1 0

################################################################################
#### VISUALISATION
################################################################################

# Generate a spectrogram (output to spectrogram.png)
sox speech.wav -n spectrogram
```

```shell
rev1-sp0.9-187_003_0793 flac -c -d -s ./speechDATA/train_data_01/003/187/187_003_0793.flac | sox -t wav - -t wav - speed 0.9 | wav-reverberate --shift-output=true --impulse-response="sox RIRS_NOISES/simulated_rirs/smallroom/Room065/Room065-00026.wav -r 16000 -t wav - |" --additive-signals='sox RIRS_NOISES/pointsource_noises/noise-free-sound-0687.wav -r 16000 -t wav - | wav-reverberate --impulse-response="sox RIRS_NOISES/simulated_rirs/smallroom/Room065/Room065-00027.wav -r 16000 -t wav - |"  - - |,sox RIRS_NOISES/pointsource_noises/noise-free-sound-0455.wav -r 16000 -t wav - | wav-reverberate --impulse-response="sox RIRS_NOISES/simulated_rirs/smallroom/Room065/Room065-00092.wav -r 16000 -t wav - |"  - - |,sox RIRS_NOISES/pointsource_noises/noise-free-sound-0777.wav -r 16000 -t wav - | wav-reverberate --impulse-response="sox RIRS_NOISES/simulated_rirs/smallroom/Room065/Room065-00028.wav -r 16000 -t wav - |"  - - |' --start-times='9.11,0.06,6.27' --snrs='20.0,0.0,5.0'  - - |

```

