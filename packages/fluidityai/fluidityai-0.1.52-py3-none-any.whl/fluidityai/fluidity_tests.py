import unittest
from datetime import datetime as dt
import string

# Prerequisites
# pip install fluidityai
# pip install numpy==1.26.4
from fluidityai import LLM, llmCache, Task, Workflow

# Remember to set the environment variable OPENAI_API_KEY to your Open AI key token
from openai import OpenAI
llmCache.addLLM("OPENAI:gpt-4o-mini", LLM(OpenAI(), "gpt-4o-mini"))
llmCache.addLLM("OPENAI:gpt-4o", LLM(OpenAI(), "gpt-4o"))
llmCache.setDefault("OPENAI:gpt-4o")

def is_valid_date(date_str, date_fmt):
    try:
        dt.strptime(date_str, date_fmt)
        return True
    except ValueError:
        return False

def clean_lower_str(text):
    cleaned_text = text.strip(string.punctuation)
    return cleaned_text.lower()

print("Setting up workflow")
w = Workflow("Monarchs")

t1 = Task(
    name="King",
    instructions="Please give me the name of a famous 18th century king",
    role="You are an AI historian"
    # output_type is "string" by default
)
t2 = Task(
    name="Queen",
    instructions="Please give me the name of a famous 18th century queen",
    role="You are an AI historian"
) 
t3 = Task(
    name="DOB",
    instructions="Please tell me the dates of birth of {King} and {Queen} in the format dd-Mmm-yyyy",
    role="You are an AI historian",
    output_type="dict"
)
t4 = Task(
    name="Older",
    instructions="Please tell me which of these two monarchs was older, given their dates of birth: {DOB}"
)

t1.setNextTask("Queen")
t2.setNextTask("DOB")
t3.setNextTask("Older")
w.addTasks(t1, t2, t3, t4)

print("Running workflow...")
w.run("King")
monarchs_dict = w.outputs()

print("Running tests...")

class TestWorkflow(unittest.TestCase):
    def test_Task1(self):
        self.assertGreater(len(monarchs_dict["King"]), 0)

    def test_Task2(self):
        self.assertGreater(len(monarchs_dict["Queen"]), 0)

    def test_Task3(self):
        self.assertTrue(is_valid_date(monarchs_dict["DOB"][monarchs_dict["King"]], '%d-%b-%Y'))
        self.assertTrue(is_valid_date(monarchs_dict["DOB"][monarchs_dict["Queen"]], '%d-%b-%Y'))

    def test_Task4(self):
        self.assertTrue(
            clean_lower_str(monarchs_dict["Older"]) in
            [clean_lower_str(monarchs_dict["King"]), clean_lower_str(monarchs_dict["Queen"])]
        )

unittest.main()
