import pandas as pd
import ast
import re


def read_output():
    with open("../output.txt", "r") as f:
        stringData = f.readlines()
        data = [ast.literal_eval(line.strip()) for line in stringData]
    return data

def clean_email(text):
    text = re.sub(r'(?i)subject:', '', text)            
    text = re.sub(r'(?i)sent from my .*', '', text)     
    text = re.sub(r'\n+', ' ', text)                    
    text = re.sub(r'\s+', ' ', text)                    
    text = text.strip()
    return text

# Assuming first email of the conversation is the root issue
def collect_root_emails():
    conversations = read_output()
    issues = []
    for convo in conversations:
        root_email = convo[-1]
        issue = root_email["subject"] + " " + root_email["body"]
        issue = clean_email(issue)
        issues.append(issue)
    return issues


