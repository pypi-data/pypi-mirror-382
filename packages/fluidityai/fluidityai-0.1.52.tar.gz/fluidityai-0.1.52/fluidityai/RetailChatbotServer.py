import sys
import importlib
import pandas as pd
import duckdb as db
import json

import socket
import threading

from fluidityai import Utils, WebUtils, LLM, llmCache, Task, Workflow, ChatbotTask, FileLoaderTask, UserInputTask, PasswordInputTask

from openai import OpenAI
llmCache.addLLM("OPENAI:gpt-4o-mini", LLM(OpenAI(), "gpt-4o-mini"))
llmCache.setDefault("OPENAI:gpt-4o-mini")

DATAFILE_DIR="/Users/ashthakur/GenAI/datafiles/"

# Basic WebSocket server
HOST = '127.0.0.1'
PORT = 12345

def get_workflow(client_socket):
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
    
    chat_workflow.setRemoteClient(client_socket)
    return chat_workflow

def handle_client(client_socket, client_address):
    print(f"Connection from {client_address}")

    # Perform the handshake
    request = client_socket.recv(1024).decode()
    headers = WebUtils.parse_headers(request)
    if 'Sec-WebSocket-Key' not in headers:
        client_socket.close()
        return

    accept_key = WebUtils.generate_accept_key(headers['Sec-WebSocket-Key'])
    handshake_response = (
        'HTTP/1.1 101 Switching Protocols\r\n'
        'Upgrade: websocket\r\n'
        'Connection: Upgrade\r\n'
        f'Sec-WebSocket-Accept: {accept_key}\r\n\r\n'
    )
    client_socket.sendall(handshake_response.encode())
    print(f"Handshake completed with {client_address}")

    # Now build and start the chat workflow
    try:
        workflow = get_workflow(client_socket)
        workflow.setFirstTask("Loader")
        workflow.run()

    except Exception as e:
        print(f"Error with {client_address}: {e}")

    finally:
        client_socket.close()
        print(f"Connection closed with {client_address}")

# Start server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"Listening on ws://{HOST}:{PORT}")

    while True:
        client_sock, addr = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_sock, addr))
        client_thread.start()
