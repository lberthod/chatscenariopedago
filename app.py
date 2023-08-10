#-*- mode: python -*-
# -*- coding: utf-8 -*-
 # loic.berthod@hevs.ch /lberthod@gmail.com
 # python script : openai chatgpt 3-5, whister, pyttsx3, ai text to speak
 # do the pip install you need
 # pip install sounddevice soundfile numpy openai colorama pydub fpdf pyttsx3 langchain pyrebase
 # need to have a chatbot.txt et openaiapikey.txt
 # -*- coding: utf-8 -*-
import streamlit as st
from gtts import gTTS

import sounddevice as sd
import soundfile as sf
import numpy as np
import openai
import os
import requests
import re
from colorama import Fore, Style, init
import datetime
import base64
from pydub import AudioSegment
from pydub.playback import play
import time
import string
from fpdf import FPDF
 
import pyttsx4
import pyrebase

 # ceci est les import langchain pour gerer la gestion avec les prompts et memoire
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain 
from langchain.memory import ConversationBufferMemory
from langchain.utilities import SerpAPIWrapper
from langchain.agents import Tool
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool

import pyrebase
from elevenlabs import generate, play

from elevenlabs import set_api_key

engine = pyttsx4.init()

set_api_key("5042302e16f8a2c59a077fd896ea614e")
os.environ['OPENAI_API_KEY'] = "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"
 


rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate
engine.setProperty('rate', 125)     # setting up new voice rate
voices = engine.getProperty('voices')

volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
print (volume)                          #printing current volume level
engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1
voices = engine.getProperty('voices')       #getting details of current voice
#engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
engine.setProperty('voice', voices[38].id)   #changing index, changes voices. 1 for female

 
init()
# Typical non-streaming request
start_time = time.time()

 
config = {
    "apiKey": "AIzaSyAZ9NNn6W2WOX3JY5-tswLX8fm9OOfH7Z0",
    "authDomain": "chatbotsoloia.firebaseapp.com",
    "projectId": "chatbotsoloia",
    "databaseURL": "https://chatbotsoloia-default-rtdb.europe-west1.firebasedatabase.app/",
    "storageBucket": "chatbotsoloia.appspot.com",
    "messagingSenderId": "305385169995",
    "appId": "1:305385169995:web:2adb0ef70c1dd310a159ce",
    "measurementId": "G-Y15MRTZ33Z"
}
 
firebase = pyrebase.initialize_app(config)
db = firebase.database()
 
 
# Prompt templates
question1a_template = PromptTemplate(
    input_variables = ['question1'], 
    template="Instructions : Vous allez recevoir un message.  Votre tâche consiste à de redonner uniquement les mot du nom de famille    Sans information complémentaire. Voici le retour du questionnaire : {question1}")

question1b_template = PromptTemplate(
    input_variables = ['question1'], 
    template="Instructions : Vous allez recevoir un message .  Votre tâche consiste à de redonner uniquement le prénom.   Sans information complémentaire, que le prénom. Voici le retour du questionnaire : {question1}")
 
question2_template = PromptTemplate(
    input_variables = ['question2'], 
    template="Instructions : Vous allez recevoir un message contenant un âge.  Votre tâche consiste à la redonner en ayant que le chiffre approprié pour  l'enregistrement dans une base de données Firebase en temps réel. Voici le retour du questionnaire : {question2}")

question3_template = PromptTemplate(
    input_variables = ['question3'], 
    template="Instructions : Vous allez recevoir un message contenant un genre.  Votre tâche consiste à la redonner en un mot ( femme ou homme ou autre).  Sans information complémentaire, que le genre.  Voici le retour du questionnaire : {question3}")


question4_template = PromptTemplate(
    input_variables = ['question4'], 
    template="Instructions : Vous allez recevoir un message contenant une réponse oui ou non.  Votre tâche consiste à la redonner en un mot ( oui ou non).  Sans information complémentaire, que le mot.  Voici le retour du questionnaire : {question4}")

question5_template = PromptTemplate(
    input_variables = ['question4'], 
    template="Instructions : Vous allez recevoir un message contenant une réponse oui ou non.  Votre tâche consiste à la redonner en un mot ( oui ou non).  Sans information complémentaire, que le mot.  Voici le retour du questionnaire : {question4}")

question6_template = PromptTemplate(
    input_variables = ['question4'], 
    template="Instructions : Vous allez recevoir un message contenant une réponse oui ou non.  Votre tâche consiste à la redonner en un mot ( oui ou non).  Sans information complémentaire, que le mot.  Voici le retour du questionnaire : {question4}")


# Memory 
question1_memory = ConversationBufferMemory(input_key='question1', memory_key='question1_memory')
question2_memory = ConversationBufferMemory(input_key='question2', memory_key='question2_memory')
question3_memory = ConversationBufferMemory(input_key='question3', memory_key='question3_memory')
question4_memory = ConversationBufferMemory(input_key='question4', memory_key='question4_memory')
question5_memory = ConversationBufferMemory(input_key='question5', memory_key='question5_memory')
question6_memory = ConversationBufferMemory(input_key='question6', memory_key='question6_memory')

 
# Llms
llm = OpenAI(temperature=0.9) 
question1a_chain = LLMChain(llm=llm, prompt=question1a_template, verbose=True, output_key='question1a_output', memory=question1_memory)
question1b_chain = LLMChain(llm=llm, prompt=question1b_template, verbose=True, output_key='question1b_output', memory=question1_memory)
question2_chain = LLMChain(llm=llm, prompt=question2_template, verbose=True, output_key='question2_output', memory=question2_memory)
question3_chain = LLMChain(llm=llm, prompt=question3_template, verbose=True, output_key='question3_output', memory=question3_memory)
question4_chain = LLMChain(llm=llm, prompt=question4_template, verbose=True, output_key='question4_output', memory=question4_memory)
question5_chain = LLMChain(llm=llm, prompt=question5_template, verbose=True, output_key='question5_output', memory=question5_memory)
question6_chain = LLMChain(llm=llm, prompt=question6_template, verbose=True, output_key='question6_output', memory=question6_memory)

 
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
 
def val():
    val = val + 1 
    return val
def incrementer_compteur():
    # On définit une variable compteur qui gardera sa valeur entre les appels à la fonction grâce au mot-clé 'nonlocal'.
    # Si la variable n'existe pas encore, elle est créée avec une valeur de 0.
    global compteur
    compteur += 1  # On incrémente le compteur de 1 à chaque passage.
    return compteur
 
# On initialise le compteur à 0 avant d'appeler la fonction.
compteur = 0
api_key = "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"

def speak(text1):
    if(2 == 1) :
        test = text1
        audio = generate(
        text=test,
        voice="Arnold",
        model='eleven_multilingual_v1'
        )   

        play(audio)
    engine.say(text1)
    engine.runAndWait()
    engine.stop()

 
def addDialogue1(message):
    valeur_finale = incrementer_compteur()
    information = "Kevin : " + message
    data = {valeur_finale: information}
 #   db.child("Dialogue").child("1").set(data)
    db.child("Dialogue").child("1").update(data)
 
    return ""
 
 
def record_and_transcribe(fs=44100):
    duration = 10.5  # seconds
    print('Recording...')
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    print('Recording complete.')
    filename = 'myrecording.wav'
    sf.write(filename, myrecording, fs)
    with open(filename, "rb") as file:
        openai.api_key = api_key
        result = openai.Audio.transcribe("whisper-1", file)
    transcription = result['text']
    print(transcription)
    return transcription

def finalfunc():
            speak("Quelle est votre nom et prénom?")
            st.write("Quelle est votre nom et prénom?")
            question1 = record_and_transcribe()
            st.write(question1)
            question1a_output = question1a_chain.run(question1)
            st.write("q1" + question1a_output)

            question1b_output = question1b_chain.run(question1)
            st.write("q1b" + question1b_output)
            
            
            speak("Pourriez-vous me dire quel est votre âge?")
            st.write("Pourriez-vous me dire quel est votre âge?")
            question2 = record_and_transcribe()
            st.write(question2)
            question2_output = question2_chain.run(question2)
            st.write(question2_output)
            
            speak("Concernant votre genre, êtes-vous une femme, un homme ou autre?")
            st.write("Concernant votre genre, êtes-vous une femme, un homme ou autre?")
            question3 = record_and_transcribe()
            st.write(question3)
            question3_output = question3_chain.run(question3)
            st.write(question3_output)            
            speak("Avez-vous un diagnostic médical? ")
            st.write("Avez-vous un diagnostic médical? ")
            question4 = record_and_transcribe()
            st.write(question4)
            question4_output = question4_chain.run(question4)
            st.write(question4_output)          
            
if __name__ == "__main__":

    # L'interface utilisateur de Streamlit
    st.title("Dialogue avec GPT-3.5")
    
    rep_human = "Pose la première question de la liste "
    if st.button('Commencer le questionnaire'):
        
        
        MAX_ITERATIONS = 1
        for _ in range(MAX_ITERATIONS):
            speak("Quelle est votre nom et prénom?")
            st.write("Quelle est votre nom et prénom?")
            question1 = record_and_transcribe()
            st.write(question1)
            question1a_output = question1a_chain.run(question1)
            st.write("q1" + question1a_output)

            question1b_output = question1b_chain.run(question1)
            st.write("q1b" + question1b_output)
            
            
            speak("Pourriez-vous me dire quel est votre âge?")
            st.write("Pourriez-vous me dire quel est votre âge?")
            question2 = record_and_transcribe()
            st.write(question2)
            question2_output = question2_chain.run(question2)
            st.write(question2_output)
            
            speak("Concernant votre genre, êtes-vous une femme, un homme ou autre?")
            st.write("Concernant votre genre, êtes-vous une femme, un homme ou autre?")
            question3 = record_and_transcribe()
            st.write(question3)
            question3_output = question3_chain.run(question3)
            st.write(question3_output)            
            speak("Avez-vous un diagnostic médical? ")
            st.write("Avez-vous un diagnostic médical? ")
            question4 = record_and_transcribe()
            st.write(question4)
            question4_output = question4_chain.run(question4)
            st.write(question4_output)     

            speak("Merci de répondre au prochaine question par : Oui,  Non, mais ne représente pas un problème, Non. Une solution doit être mise en place ")
            st.write("Merci de répondre au prochaine question par : Oui,  Non, mais ne représente pas un problème, Non. Une solution doit être mise en place ")
            speak(" AVEZ-VOUS LA ossibilité de VOUS rendre de manière indépendante chez les membres de votre famille ne vivant pas dans le même logement? ")
            st.write(" Possibilité de se rendre de manière indépendante chez les membres de sa famille ne vivant pas dans le même logement ")
            question5 = record_and_transcribe()
            st.write(question5)
            question5_output = question5_chain.run(question5)
            st.write(question5_output)
