# Bring in deps
import os 
from apikey import apikey 

import streamlit as st 
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain 
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper 

os.environ['OPENAI_API_KEY'] = apikey

# App framework
st.title('🦜🔗 Scénario pédagogique')
prompt = st.text_input('Plug in your prompt here') 

# Prompt templates
title_template = PromptTemplate(
    input_variables = ['topic'], 
    template='ecris moi le titre du cours pour ce sujet : {topic}'
)

script_template = PromptTemplate(
    input_variables = ['title', 'wikipedia_research'], 
    template='ecris moi les contenus du cours  : {title} en te basant sur les ressources suivantes :{wikipedia_research} '
)

evaluation_template = PromptTemplate(
    input_variables = ['topic' ], 
    template='ecris moi les evaluation pour le cours  : {topic} en te basant une evaluation en pédagogie 360 basé sur l analyse des compétences '
)

# Memory 
title_memory = ConversationBufferMemory(input_key='topic', memory_key='chat_history')
script_memory = ConversationBufferMemory(input_key='title', memory_key='chat_history')
evaluation_memory = ConversationBufferMemory(input_key='topic', memory_key='chat_history')


# Llms
llm = OpenAI(temperature=0.9) 
title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True, output_key='title', memory=title_memory)
script_chain = LLMChain(llm=llm, prompt=script_template, verbose=True, output_key='script', memory=script_memory)
evaluation_chain = LLMChain(llm=llm, prompt=evaluation_template, verbose=True, output_key='title', memory=evaluation_memory)

wiki = WikipediaAPIWrapper()

# Show stuff to the screen if there's a prompt
if prompt: 
    title = title_chain.run(prompt)
    wiki_research = wiki.run(prompt) 
    script = script_chain.run(title=title, wikipedia_research=wiki_research)
    evaluation = evaluation_chain.run(prompt)

    st.write(title) 
    st.write(script) 
    st.write(evaluation) 

    with st.expander('Titre du cours'): 
        st.info(title_memory.buffer)

    with st.expander('Résumé du cours'): 
        st.info(script_memory.buffer)

    with st.expander('Evaluation du cours'): 
        st.info(evaluation_memory.buffer)
