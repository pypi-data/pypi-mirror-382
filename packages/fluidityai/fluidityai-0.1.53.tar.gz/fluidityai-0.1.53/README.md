## Fluidity

### Introduction
Fluidity is a set of classes written in Python to enable you to build AI workflows simply and intuitively. Basically, you create a workflow and add tasks to it. Each task points to its next task - alternatively, branch objects can be added to the workflow to programmatically decide where to go next by setting the "next_task" pointer. This way potentially complex workflow graphs, which can include cycles, can be constructed easily.

### Task types
A task can be either a *code* task (i.e. Python instructions executed locally) or an *LLM* task, meaning (natural language) instructions are sent to a large language model. The output type of each task can be specified as *string* (the default), *num* (an integer or decimal number), *json* (a JSON string), *list*, or *dict* (i.e. a dictionary). To refer to a task's output value(s) in LLM instructions, use the "{}" notation: {TaskName} for string, num or json types and an entire list or dictionary or {TaskName:n} and {TaskName:KeyName} for a specific list or dictionary element.

In Python code (i.e. for code tasks) use task_outputs["TaskName"], task_outputs["TaskName"][n] and task_outputs["TaskName"]["KeyName"] respectively.

**For example:**

<small>w = Workflow("Monarchs")\
t1 = Task(name="King", instructions="Please give me the name of a famous king", output_type="string")\
t2 = Task(name="Queen", instructions="Please give me the name of a famous queen", output_type="string")\
t3 = Task(name="DOB", instructions="Please tell me the dates of birth of {King} and {Queen} in the format dd-Mmm-yyyy", output_type="dict")\
t4 = Task(name="Older", instructions="Please tell me which of these two monarchs was older, given their dates of birth: {DOB}")\
t1.setNextTask("Queen")\
t2.setNextTask("DOB")\
t3.setNextTask("Older")\
w.addTasks(t1, t2, t3, t4)\
w.run("King")
</small>

After the above routine runs, {Older} or task_outputs["Older"] will be the name of the older monarch for subsequent LLM and code tasks respectively. You can run and test the actual code in fluidity_tests.py.

### Classes
This section consists of a brief introduction to each of the classes in the Fluidity package. Note that the package includes many useful subclasses of the Task class for e.g. file loading, user input/form processing and RAG.

**LLM, LLMCache, llmCache global instance**
Use these to set up your LLM connections and specify a default. Any task can override the default LLM with its own instance. See fluidity_examples.py lines 11-13.

**Utils and WebUtils**
Helper functions for text processing and network operations.

**Task**
This class is where the work is done: add instances of it to your Workflow (see below) object to send a request to an LLM or execute Python code locally. The constructor takes these arguments:\
*name* [required]: the name of the task. It's also the label for the task's output elsewhere in the workflow.\
*instructions* [required]: Natural language intructions for the LLM, Python code or 'file:\<Python code filepath\>'. If Python code, it is executed dynamically. It is required to set the *result* (i.e. the task's output value) and *next_task* variables in the code. *next_task* can be set to 'STOP' to terminate the workflow run.\
*role* [optional]: How should the LLM behave? e.g. 'You are an AI legal assistant specialising in family law enquiries'.\
*output_type* [optional - 'string' (default), 'num', 'json', 'list' or 'dict']\
*llm_or_code* [optional - 'llm' (default) or 'code']: Describes instructions\
*llm* [optional]: overrides the default LLM connection\
The *setNextTask("<task_name>")* function allows you to build your graph.

**TaskGroup**
Executes tasks in parallel. Add tasks to a task group instance, then add the task group to a workflow. See lines 18-72 in fluidity_examples.py

**Branch**
Set *name* and *instructions* (Python code) in the constructor, then add to a workflow like a task. It is required to set the *next_task* variable in the code - set it to 'STOP' to terminate the workflow run.

**Workflow**
Add tasks and branches to a workflow object. Either *setFirstTask("<first_task_name>")* and *run()*, or run with *run("<first_task_name>")*.

**UserInputTask**
Subclass of Task. Makes repeated command line or web chat requests until user enters the information required in a recognisable format. See fluidity_examples.py lines 74-164. Uses an LLM call to extract the required field from natural language.

**PasswordInputTask**
Subclass of Task. Asks the user to input 3 randomly chosen characters from the password. Provide Python code instructions to implement obtaining the password, possibly from a database. See fluidity_examples.py lines 74-164.

**FileLoaderClass**
Loads and caches CSV files as DataFrames; any other file types are read into a string, e.g. PDF, .txt files. Construct with *name* and *files,* a filename => filepath dictionary. See fluidity_examples.py lines 74-164.

**RAGRetrievalTask**
Chunks all pre loaded files, creates vector embeddings and stores them in an in-memory vector database, then creates
a context from the *top_pct* (10% by default) of chunks by relevance to the (pre loaded) query. Construct with *name*, name of the file *loader* and *query*, i.e. if query='My Question' then it reads task_outputs['My Question']. See fluidity_examples.py lines 198-241.

**RAGCache**
Not a task, but a useful global cache class for e.g. chat apps in which all threads query the same files.

**ChatbotTask**
Makes repeated cmd line or web chat requests for submission to the LLM. See fluidity_examples.py lines 74-164. The ChatbotTask constructor takes the following arguments:\
*name* [required]: the task name\
*response* [optional]: the name of the task answering the question\
*prompt* [required]: the initial message or prompt to the user\
*toxicMsg* [required]: the reponse given to offensive or potentially harmful input, e.g. hacking attempts\
*greeting* [optional - False (default) or True]: greet user with Good morning/afternoon/evening?\
*initialPromptOnly* [optional - False (default) or True]: is *prompt* displayed only the first time?

**FormTask**
Requests the LLM to extract specific information fields from natural language text. See fluidity_examples.py lines 243-326 for usage.

**FormFillTask**
Fills form fields by processing the response from the LLM. See fluidity_examples.py lines 243-326 and the task code file taxi.py for usage.
