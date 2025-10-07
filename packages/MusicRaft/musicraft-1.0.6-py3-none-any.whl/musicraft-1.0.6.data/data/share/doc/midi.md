# MusicRaft
## Midi support
Note: this all refers to MIDI playback/synthesis. MIDI input devices (keyboards etc.)
are not supported at all.

Musicraft creates and re-creates MIDI files on the fly by running `abc2midi` 
each time the ABC file is changed . This MIDI file can be played using the 
`MIDI` entry menu of the  top menu bar. As each note is played, the corresponding note
(or rest) symbol in the score is highlighted with a red circle.
This can be is very handy.

Musicraft uses the
[MIDO](https://mido.readthedocs.io/en/latest/index.html)
package with the usual backend - `rtmdi`.

MIDI output works on Windows 10 with the standard
Microsoft GS wavetable software synthesizer.

Midi output also worked fine On Mac OSX, but I first needed to (build and!)
start `simplesynth`.

I currently use the midi synthesiser 'fluidsynth' under Mx Linux.

My older test environment for MIDI suport is to have the Timidity
synthesiser running as a 'daemon' on an (Ubuntu) Linux platform.

This showed up as follows:

`gill@luna:/tera/gill/PycharmProjects/MusicRaft$ ps ax | grep timidity
 1388 ?        S      1:53 timidity -iA -B2,8 -Os
11403 pts/0    S+     0:00 grep --color=auto timidity
gill@luna:/tera/gill/PycharmProjects/MusicRaft$ `

The default behaviour ounder Linux, however, seems to be to expect
and assume real MIDI hardware. Hence, in order to direcet the output
through  `timidity`, I have to change the setting by either ...
* using the `Midi` --> `select MIDI output` dialogue

...or...
* using a variant start-up script which overrules the default setting.


 