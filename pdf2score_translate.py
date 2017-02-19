# -*- coding:Utf-8 -*-
#!/usr/bin/env python
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree

class Score:
    def __init__(self, file_input, voices, nb_voice):
        self.voices = voices
        self.nb_voice = nb_voice
        self.file_input = file_input
    
    def addVoice(self, voice):
        self.voices.append(voice)
        self.nb_voice = self.nb_voice + 1

class Voice:
    def __init__(self, name, notes, nb_notes):
        self.name = name
        self.nb_notes = nb_notes
        self.notes = notes
        self.voidBar = []
    
    def addNote(self, note):
        self.notes.append(note)
        self.nb_notes = self.nb_notes + 1
    
    def countBar(self):
        nb_bar = 1
        for i in range(len(self.notes)):
            nb_bar = max(int(self.notes[i].bar_id), nb_bar)
        for i in range(len(self.voidBar)):
            nb_bar = max(int(self.voidBar[i]), nb_bar)
        self.nb_bar = nb_bar + 1
    
    def addVoidBar(self, bar_id):
        self.voidBar.append(bar_id)

class Note:
    def __init__(self, x, y, staff_position, name, octave, chord, bar_id):
        self.x = x
        self.y = y
        self.staff_position = staff_position
        self.name = name
        self.octave = octave
        self.chord = chord
        self.bar_id = bar_id
    
    def setKey(self, key):
        self.key = key
    
    def setClef(self, clef):
        self.clef = clef
    
    def setVoice(self, voice):
        self.voice = voice
    

nom_fichier = 'mendelssohn'
input_lily = ElementTree.parse(nom_fichier + '_input_lily.xml')
input_lily_root = input_lily.getroot()

# creation of the score
thisScore = Score(nom_fichier + '_input_lily.xml', [], 0)

for voice in input_lily_root.findall('./voice'):
    voice_name = voice.find('name').text
    currentVoice = Voice(voice_name, [], 0)
    for staff in voice.findall('./staff'):
        staff_position = staff.find('position').text
        key = staff.find('key').text
        clef = staff.find('clef').text
        for bar in staff.findall('./bar'):
            bar_id = bar.find('bar_id').text
            num_note = 0
            for note in bar.findall('./note'):
                x_note = note.find('x').text
                y_note = note.find('y').text
                note_name = note.find('name').text
                octave = note.find('octave').text
                chord = note.find('chord').text
                thisNote = Note(x_note, y_note, staff_position, note_name, octave, chord, bar_id)
                thisNote.setKey(key)
                thisNote.setClef(clef)
                thisNote.setVoice(voice_name)
                currentVoice.addNote(thisNote)
                num_note = num_note + 1
            if num_note == 0:
                currentVoice.addVoidBar(bar_id)
    thisScore.addVoice(currentVoice)

thisScore.voices[0].countBar()
print(thisScore.voices[0].nb_bar)
