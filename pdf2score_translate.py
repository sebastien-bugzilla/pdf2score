# -*- coding:Utf-8 -*-
#!/usr/bin/env python
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree
from operator import itemgetter, attrgetter, methodcaller

class Score:
    def __init__(self, file_input, voices, nb_voice):
        self.voices = voices
        self.nb_voice = nb_voice
        self.file_input = file_input
    
    def addVoice(self, voice):
        self.voices.append(voice)
        self.nb_voice = self.nb_voice + 1

class Voice:
    def __init__(self, name, chords, nb_chords):
        self.name = name
        self.nb_chords = nb_chords
        self.chords = chords
        self.voidBar = []
        self.key = ""
        self.clef = ""
    
    def addChord(self, chord):
        self.chords.append(chord)
        self.nb_chords = self.nb_chords + 1
        if self.key == "":
            self.key = self.chords[0].notes[0].key
        if self.clef == "":
            self.clef = self.chords[0].notes[0].clef
    
    def countBar(self):
        nb_bar = 1
        for i in range(len(self.chords)):
            nb_bar = max(int(self.chords[i].notes[0].bar_id), nb_bar)
        for i in range(len(self.voidBar)):
            nb_bar = max(int(self.voidBar[i]), nb_bar)
        self.nb_bar = nb_bar + 1
    
    def addVoidBar(self, bar_id):
        self.voidBar.append(bar_id)
    
    def defineOctave(self):
        previous_offset = 0
        for i in range(self.nb_chords):
            self.chords[i].rankNote()
            self.chords[i].chordPosition(previous_offset)
            previous_offset = int(self.chords[i].notes[0].offset)
    
    def keyTranslation(self):
        key_es = ['c','f','bes','ees','aes','des','ges','ces']
        key_is = ['c','g','d','a','e','b','fis','cis']
        if len(self.key) == 1:
            index_key = 0
        else:
            index_key = int(self.key[0])
            key_type = self.key[1:3]
        if key_type == "es":
            temp = "\\key " + str(key_es[index_key]) + " \\major\n"
        else:
            temp = "\\key " + str(key_is[index_key]) + " \\major\n"
        self.translation = self.translation + temp
    
    def clefTranslation(self):
        temp = ""
        if self.clef == "g2":
            temp = "\\relative c'' {\n\t\\clef treble\n\t"
        elif self.clef == "c3":
            temp = "\\relative c' {\n\t\\clef alto\n\t"
        elif self.clef == "f4":
            temp = "\\relative c {\n\t\\clef bass\n\t"
        elif self.clef == "c2":
            temp = "\\relative c' {\n\t\\clef mezzosoprano\n\t"
        elif self.clef == "f3":
            temp = "\\relative c {\n\t\\clef varbaritone\n\t"
        elif self.clef == "c1":
            temp = "\\relative c'' {\n\t\\clef soprano\n\t"
        elif self.clef == "c4":
            temp = "\\relative c' {\n\t\\clef tenor\n\t"
        self.translation = temp
    
    def voiceTranslation(self):
        temp = self.translation
        numBar = 0
        temp = temp + str("\n% mesures ") + str(numBar + 1) + \
            str(" à ") + str(numBar + 5) + str("\n\t")
        for i in range(self.nb_chords):
            bar_id = int(self.chords[i].notes[0].bar_id)
            if numBar <> bar_id:
                while numBar <> bar_id:
                    numBar = numBar + 1
                    if numBar%5 ==0 :
                        temp = temp + "\n"
                    else:
                        temp = temp + "\n\t"
                    if numBar%5 == 0:
                        temp = temp + str("% mesures ") + str(numBar + 1) + \
                            str(" à ") + str(numBar + 5) + str("\n\t")
            self.chords[i].translate()
            temp = temp + str(self.chords[i].translation) + " "
            
        temp = temp + "\n}\n"
        self.translation = temp

class Note:
    def __init__(self, x, y, staff_position, name, offset, bar_id):
        self.x = x
        self.y = y
        self.staff_position = staff_position
        self.name = name
        self.offset = offset
        self.bar_id = bar_id
    
    def setKey(self, key):
        self.key = key
    
    def setClef(self, clef):
        self.clef = clef
    
    def setVoice(self, voice):
        self.voice = voice
    
    def notePosition(self, previous_offset):
        distance = int(self.offset) - previous_offset
        if distance > 0:
            if distance < 4:
                self.suffixe = ""
            elif (distance >= 4 and distance < 11):
                self.suffixe = "'"
            elif (distance >= 11 and distance < 18):
                self.suffixe = "''"
            elif (distance >= 18 and distance < 25):
                self.suffixe = "'''"
        else:
            if distance > -4:
                self.suffixe = ""
            elif (distance > -11 and distance <= -4):
                self.suffixe = ","
            elif (distance > -18 and distance <= -11):
                self.suffixe = ",,"
            elif (distance > -25 and distance <= -18):
                self.suffixe = ",,,"
    

class Chord:
    def __init__(self):
        self.notes = []
        self.nb_notes = 0
        self.key = ""
        self.clef = ""
    
    def setKey(self, key):
        self.key = key
    
    def setClef(self, clef):
        self.clef = clef
    
    def setVoice(self, voice):
        self.voice = voice
    
    def addNote(self, note):
        self.notes.append(note)
        self.nb_notes = self.nb_notes + 1
    
    def rankNote(self):
        if self.nb_notes > 1:
            array = []
            for i in range(self.nb_notes):
                array.append([float(self.notes[i].y), self.notes[i]])
            array_sorted = sorted(array, key=itemgetter(0), reverse=True)
            self.notes=[]
            for i in range(self.nb_notes):
                self.notes.append(array_sorted[i][1])
    
    def chordPosition(self, previous_offset):
        if self.nb_notes == 1:
            self.notes[0].notePosition(previous_offset)
        else:
            previous_offset_chord = previous_offset
            for i in range(self.nb_notes):
                self.notes[i].notePosition(previous_offset_chord)
                previous_offset_chord = int(self.notes[i].offset)
    
    def translate(self):
        if self.nb_notes == 1:
            note_name = self.notes[0].name
            note_height = self.notes[0].suffixe
            self.translation = str(note_name) + str(note_height)
        else:
            temp = "<"
            for i in range(self.nb_notes):
                note_name = self.notes[i].name
                note_height = self.notes[i].suffixe
                temp = temp + str(note_name) + str(note_height) + " "
            temp = temp + ">"
            self.translation = temp

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
            num_chord = 0
            x_note_old = 0.
            previous_note_is_chord = "no"
            for note in bar.findall('./note'):
                x_note = note.find('x').text
                y_note = note.find('y').text
                note_name = note.find('name').text
                offset = note.find('offset').text
                chord = note.find('chord').text
                thisNote = Note(x_note, y_note, staff_position, note_name, offset, bar_id)
                thisNote.setKey(key)
                thisNote.setClef(clef)
                thisNote.setVoice(voice_name)
                if chord == "no":
                    if previous_note_is_chord == "yes":
                        currentVoice.addChord(thisChord)
                    thisChord = Chord()
                    thisChord.addNote(thisNote)
                    currentVoice.addChord(thisChord)
                    previous_note_is_chord = "no"
                else:
                    if abs(float(x_note) - x_note_old) < 1.:
                        thisChord.addNote(thisNote)
                        previous_note_is_chord = "yes"
                    else:
                        if previous_note_is_chord == "yes":
                            currentVoice.addChord(thisChord)
                        thisChord = Chord()
                        thisChord.addNote(thisNote)
                        previous_note_is_chord = "yes"
                x_note_old = float(x_note)
                num_chord = num_chord + 1
            if num_chord == 0:
                currentVoice.addVoidBar(bar_id)
    thisScore.addVoice(currentVoice)

ly_file = open(nom_fichier + "_lily.ly", "w")
for i in range(thisScore.nb_voice):
    thisScore.voices[i].defineOctave()
    thisScore.voices[i].clefTranslation()
    thisScore.voices[i].keyTranslation()
    thisScore.voices[i].voiceTranslation()
    ly_file.write(thisScore.voices[i].translation)

#for i in range(thisScore.nb_voice):
#    print("-------------------------------\n")
#    for j in range(thisScore.voices[i].nb_chords):
#        temp = ""
#        for k in range(thisScore.voices[i].chords[j].nb_notes):
#            note_name = thisScore.voices[i].chords[j].notes[k].name
#            note_height = thisScore.voices[i].chords[j].notes[k].suffixe
#            temp = temp + str(" ") + str(note_name) + str(note_height)
#        print(temp)
