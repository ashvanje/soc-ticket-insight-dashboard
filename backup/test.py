import codecs
import csv
import os
import requests
import openai
from flask import Flask, render_template, jsonify, request
from collections import defaultdict


app = Flask(__name__)
# PwC CaaS 2023-07-10T16_08_51+0800.csv
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


conversation2 = []
prompt3 = """
# below are the jira tickets of the security operation center
# summarize the below in a few paragraphs

"""
conversation2.append({"role": "user", "content": prompt3})

response2 = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=conversation2
)

ai_response2 = response2.choices[0].message.content

print(ai_response2)

conversation2.append({"role": "user", "content": "how many individual tickets listed in total?"})


response2 = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=conversation2
)

ai_response2 = response2.choices[0].message.content

print(ai_response2)


conversation2.append({"role": "user", "content": "give me a full presentation about the tickets that i can report to boss"})


response2 = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=conversation2
)

ai_response2 = response2.choices[0].message.content

print(ai_response2)