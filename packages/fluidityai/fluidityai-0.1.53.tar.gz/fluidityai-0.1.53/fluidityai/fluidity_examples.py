import fluidity_globals

import duckdb as db
import json

# Prerequisites
# pip install fluidityai
# pip install numpy==1.26.4
from fluidityai import LLM, llmCache, Utils, Task, TaskGroup, FormTask, FormFillTask, Workflow, UserInputTask, \
    PasswordInputTask, FileLoaderTask, RAGRetrievalTask, ChatbotTask

# Remember to set the environment variable OPENAI_API_KEY to your Open AI key token
from openai import OpenAI
llmCache.addLLM("OPENAI:gpt-4o-mini", LLM(OpenAI(), "gpt-4o-mini"))
llmCache.addLLM("OPENAI:gpt-4o", LLM(OpenAI(), "gpt-4o"))
llmCache.setDefault("OPENAI:gpt-4o")

# Set your datafile directory here
DATAFILE_DIR = "/Users/ashthakur/GenAI/datafiles/"

def HAIKUS():
    poem_task1 = Task(
        name="Thatcher",
        instructions="Please compose a haiku about the British prime minister Margaret Thatcher.",
        role="You are an AI poet and cultural historian.")

    poem_task2 = Task(
        name="Cameron",
        instructions="Please compose a haiku about the British prime minister David Cameron.",
        role="You are an AI poet and cultural historian.")

    poem_task3 = Task(
        name="Starmer",
        instructions="Please compose a haiku about the British prime minister Keir Starmer.",
        role="You are an AI poet and cultural historian.")

    count_task = Task(
        name="Average Wordcount",
        instructions="""
result = 0.0
c1 = len(task_outputs['PMs-Thatcher'].split())
c2 = len(task_outputs['PMs-Cameron'].split())
c3 = len(task_outputs['PMs-Starmer'].split())
result = (c1 + c2 + c3) / 3.0
    """,
        output_type="num",
        llm_or_code="code"
    )

    haiku_workflow = Workflow("Haikus")

    # A task group runs its tasks in parallel
    my_task_group = TaskGroup("PMs")
    my_task_group.setNextTask("Average Wordcount")

    my_task_group.addTask(poem_task1)
    my_task_group.addTask(poem_task2)
    my_task_group.addTask(poem_task3)

    haiku_workflow.addTask(my_task_group)
    haiku_workflow.addTask(count_task)

    # Run workflow
    haiku_workflow.setFirstTask("PMs")
    haiku_workflow.run()

    # Display task_outputs 
    print(haiku_workflow.outputs())

    # Convert workflow object to JSON and back again
    wf_json_str = json.dumps(haiku_workflow.to_dict(), indent=4)
    print(wf_json_str)
    wf_dict = json.loads(wf_json_str)
    wf = Workflow.from_dict(wf_dict)
    print(json.dumps(wf.to_dict(), indent=4))

def RetailChatbot():
    # Set up workflow
    loader_task = FileLoaderTask(
    name="Loader",
    files={
        "Customers" : f"{DATAFILE_DIR}Customers.csv",
        "Orders" : f"{DATAFILE_DIR}Orders.csv",
        "OrderDetails" : f"{DATAFILE_DIR}OrderDetails.csv"
        }
    )

    user_name_task = UserInputTask(
        name="User Name",
        dataType="name",
        format="First_name Surname",
        prompt1="Please tell me your full name",
        prompt2="I didn't quite get your name. Please try again",
        toxicMsg="Offensive and/or potentially harmful messages will be reported - please try again",
        greeting = True
    )

    dob_task = UserInputTask(
        name="DOB",
        dataType="date",
        format="dd-Mmm-yy",
        prompt1="Now tell me your date of birth",
        prompt2="I didn't quite get that. Please try again",
        toxicMsg="Offensive and/or potentially harmful messages will be reported - please try again"
    )

    email_task = UserInputTask(
        name="Email",
        dataType="email",
        format="user@domain",
        prompt1="Now tell me your email address",
        prompt2="I didn't quite get that. Please try again",
        toxicMsg="Please enter your email address in the correct format"
    )
    email_task.setValidationFunction(Utils.is_email)

    pwd_task = PasswordInputTask(
         name="Password",
         instructions=f"file:{DATAFILE_DIR}pwd.py"
    )

    cust_orders_task = Task(
        name="Cust Orders",
        instructions=f"file:{DATAFILE_DIR}ord.py",
        llm_or_code="code"
    )

    question_task = ChatbotTask(
        name="User Question",
        response="Answer",
        prompt="Please type your question",
        toxicMsg="Offensive and/or potentially harmful messages will be reported - please try again",
        greeting=False # We have already said Good morning/afternoon etc.
    )
    
    llm_task = Task(
        name="Answer",
        instructions="Please respond to the customer's input: '{User Question}'",
        role="""
        You are an AI assistant working for an online clothes retailer. Your task is to answer any question about the customer's
        orders. Do not answer any questions on other topics. The customer's order details are attached here: {Cust Orders}
        """
    )
    
    llm_task.maintainContext()
    question_task.setNextTask("Answer")
    llm_task.setNextTask("User Question")

    loader_task.setNextTask("User Name")
    user_name_task.setNextTask("DOB")
    dob_task.setNextTask("Email")
    email_task.setNextTask("Password")
    pwd_task.setNextTask("Cust Orders")
    cust_orders_task.setNextTask("User Question")
    
    chat_workflow = Workflow("Chat")

    chat_workflow.addTask(loader_task)
    chat_workflow.addTask(user_name_task)
    chat_workflow.addTask(dob_task)
    chat_workflow.addTask(email_task)
    chat_workflow.addTask(pwd_task)
    chat_workflow.addTask(cust_orders_task)
    chat_workflow.addTask(llm_task)
    chat_workflow.addTask(question_task)
    
    chat_workflow.run("Loader")

def SimpleChatbot():
     input_task = Task(
        name="UserInput",
        instructions="""
result = ""
if "Chatbot" in task_outputs:
    print("The chatbot answered: ", task_outputs["Chatbot"])

result = input("Please type your question: ")
if result == '.':
    print("Goodbye!")
    exit()
""",
        llm_or_code = "code"
    )
     
     chat_task = Task(
          name="Chatbot",
          instructions="Please respond to the user's input: '{UserInput}'",
          role="You are an AI general knowledge assistant with a particular interest in history."
     )
     
     chat_task.maintainContext()
     input_task.setNextTask("Chatbot")
     chat_task.setNextTask("UserInput")

     chat = Workflow("Chat")
     chat.addTask(input_task)
     chat.addTask(chat_task)

     chat.run("UserInput")

def RAGTest():
    loader_task = FileLoaderTask(
    name="Loader",
    files={
            "Family Law" : f"{DATAFILE_DIR}eatons-family-law-guide.pdf"
        }
    )

    rag_question_task = ChatbotTask(
        name="RAG Question",
        response="Answer",
        prompt="Please type your question",
        toxicMsg="Offensive and/or potentially harmful messages will be reported - please try again",
        greeting=True
    )

    # Generates a context for the LLM based on the question asked and the loaded files
    rag_task = RAGRetrievalTask(
         name="Context",
         loader="Loader",
         query="RAG Question"
    )

    llm_answer_task = Task(
         name="Answer",
         instructions="Using the following context:\n{Context}\n\nAnswer the question: '{RAG Question}'.",
         role="You are an AI legal assistant skilled at answering questions on UK family law based on a given context."
    )
    
    llm_answer_task.maintainContext()

    loader_task.setNextTask("RAG Question")
    rag_question_task.setNextTask("Context")
    rag_task.setNextTask("Answer")
    llm_answer_task.setNextTask("RAG Question")

    wf = Workflow("RAG Test")
    wf.addTask(loader_task)
    wf.addTask(rag_question_task)
    wf.addTask(rag_task)
    wf.addTask(llm_answer_task)

    wf.setFirstTask("Loader")
    wf.run()

def Taxi():
    booking_fields = {
            'From': 'start address',
            'To': 'destination address',
            'FromPostcode': 'start postcode',
            'ToPostcode': 'destination postcode',
            'Date': 'travel date',
            'Time': 'travel time',
            'Session': 'part of day',
            'Passengers': 'number of passengers',
            'Luggage': 'luggage'
        }
    
    booking_fields_task = FormTask(
        name="Booking",
        fields=booking_fields,
        formats={
            'Date': 'yyyy-mm-dd',
            'Time': 'HH:mm and rounded to the nearest 10 minutes',
            'Passengers': '%d',
            'Luggage': '{luggage_item : number}'
        }
    )

    booking_fields_fill_task = FormFillTask(
        name="Booking Fill",
        formName="Booking",
        formResponseName="Fields",
        fields=booking_fields,
        validators={ 'FromPostcode': "minPostcodeLen", 'ToPostcode': "minPostcodeLen"}
    )

    journey_details_task = ChatbotTask(
        name="Journey Details",
        response="Feedback",
        prompt="Please tell me about your journey",
        toxicMsg="Offensive and/or potentially harmful messages will be reported - please try again",
        greeting=True,
        initialPromptOnly=True
    )   
    
    extract_fields_task = Task(
        name="Fields",
        instructions="""
Please extract the {Booking:Fields} from the following journey description: '{Journey Details}'. 
For relative dates, e.g. 'tomorrow', assume today's date is {Today}. If any of these values cannot be determined, please set the field
to 'Unknown'. For travel time, unless a specific time is indicated, set this field to 'Unknown'. For postcodes, if a general area is specified, return
the short postcode (up to 4 characters). If an exact location or building is provided, return the full postcode. If luggage is not mentioned, return 'Unknown',
but if the user specifies no luggage return 'None'.
""",
        role="""
You are an AI booking operator working for an online taxi firm in the UK. Your task is to study the customer's journey requirements and extract
the key details required to make a booking, e.g. travel date, number of people travelling, destination etc. and look up the postcodes of journey start and end points.
    """,
        output_type="dict"
    )
    
    feedback_task = Task(
        name="Feedback",
        llm_or_code="code",
        instructions=f"file:{DATAFILE_DIR}taxi.py",
        output_type="string"
    )

    journey_details_task.setNextTask("Booking")
    booking_fields_task.setNextTask("Fields")
    extract_fields_task.setNextTask("Booking Fill")
    booking_fields_fill_task.setNextTask("Feedback")
    feedback_task.setNextTask("Journey Details")
    
    chat_workflow = Workflow("Taxi")

    chat_workflow.addTask(journey_details_task)
    chat_workflow.addTask(booking_fields_task)
    chat_workflow.addTask(extract_fields_task)
    chat_workflow.addTask(booking_fields_fill_task)
    chat_workflow.addTask(feedback_task)

    chat_workflow.setFirstTask("Journey Details")
    chat_workflow.run()

    print(chat_workflow.outputs())


#####################
### RUN THIS CODE ###
#####################
# RetailChatbot()
HAIKUS()
# RAGTest()
# SimpleChatbot()
# AssortedTests()
# Taxi()
