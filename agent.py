from termcolor import colored
from tool_functions import basic_calculator, reverse_string, timer, summarise_text
import requests, json, aiohttp, asyncio


class OllamaModel:
    def __init__(self, model, system_prompt, temperature = 0.2, stop = None):
        """
        Initializes the OllamaModel with the given parameters.
        """
        self.model_endpoint = "http://localhost:11434/api/generate"
        self.temperature = temperature
        self.model = model
        self.system_prompt = system_prompt
        self.headers = {"Content-Type": "application/json"}
        self.stop = stop

    async def generate_text(self, prompt):
        """
        Generates a response from the Ollama model based on the provided prompt.
        """
        payload = {
            "model": self.model,
            "format": "json",
            "prompt": prompt,
            "system": self.system_prompt,
            "stream": False,
            "temperature": self.temperature,
            "stop": self.stop
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.model_endpoint, headers = self.headers, json = payload) as request_response:
                    request_response_json = await request_response.json()
                    response = request_response_json['response']
                    response_dict = json.loads(response)

                    print(f"\n\n[ollama response]: {response_dict}")

                    return response_dict
        except aiohttp.ClientError as e:
            response = {"[error]": f"Error in invoking model! {str(e)}."}
            return response
class ToolBox:
    def __init__(self):
        self.tools_dict = {}

    def store(self, functions_list):
        """
        Stores the literal name and docstring of each function in the list.

        Parameters:
        functions_list (list): List of function objects to store.

        Returns:
        dict: Dictionary with function names as keys and their docstrings as values.
        """
        for func in functions_list:
            self.tools_dict[func.__name__] = func.__doc__
        return self.tools_dict

    def tools(self):
        """
        Returns the dictionary created in store as a text string.

        Returns:
        str: Dictionary of stored functions and their docstrings as a text string.
        """
        tools_str = ""
        for name, doc in self.tools_dict.items():
            tools_str += f"{name}: \"{doc}\"\n"
        return tools_str.strip()
    
system_prompt_template = """
You are an intelligent AI assistant with access to specific tools. Your responses must ALWAYS be in this JSON format:
{{
    "tool_choice": "name_of_the_tool",
    "tool_input": "inputs_to_the_tool"
}}

TOOLS AND WHEN TO USE THEM:

1. basic_calculator: Use for ANY mathematical calculations
   - Input format: {{"num1": number, "num2": number, "operation": "add/subtract/multiply/divide"}}
   - Supported operations: add/plus, subtract/minus, multiply/times, divide
   - Example inputs and outputs:
     Input: "Calculate 15 plus 7"
     Output: {{"tool_choice": "basic_calculator", "tool_input": {{"num1": 15, "num2": 7, "operation": "add"}}}}
     
     Input: "What is 100 divided by 5?"
     Output: {{"tool_choice": "basic_calculator", "tool_input": {{"num1": 100, "num2": 5, "operation": "divide"}}}}

2. reverse_string: Use for ANY request involving reversing text
   - Input format: Just the text to be reversed as a string
   - ALWAYS use this tool when user mentions "reverse", "backwards", or asks to reverse text
   - Example inputs and outputs:
     Input: "Reverse of 'Howwwww'?"
     Output: {{"tool_choice": "reverse_string", "tool_input": "Howwwww"}}
     
     Input: "What is the reverse of Python?"
     Output: {{"tool_choice": "reverse_string", "tool_input": "Python"}}

3. timer: Use for setting a timer for a specified duration
   - Input format: The duration of the timer in seconds as a string
   - ALWAYS use this tool when user mentions "timer" or asks to set a timer or a countdown
   - Example inputs and outputs:
     Input: "Set a timer for 10 seconds"
     Output: {{"tool_choice": "timer", "tool_input": "10"}}

     Input: "Timer for 60 seconds"
     Output: {{"tool_choice": "timer", "tool_input": "60"}}

     Input: "Timer for seconds"
     Output: {{"tool_choice": "timer", "tool_input": "Error: Invalid duration. Please provide a valid number of seconds."}}

4. summarise_text: Use for summarizing text
   - Input format: The text to be summarized as a string
   - ALWAYS use this tool when user mentions "summarize" or asks to summarize text
   - Simply extract the text to be summarized from the prompt and pass it to this tool; DO NOT summarize the text yourself
   - Example inputs and outputs:
     Input: "Summarize the text: 'This is a long text that needs to be summarized.'"
     Output: {{"tool_choice": "summarise_text", "tool_input": "This is a long text that needs to be summarized."}}

     Input: "Can you summarize 'this paragraph'?"
     Output: {{"tool_choice": "summarise_text", "tool_input": "'this paragraph'"}}

     Input: "Generate a summary of this 'long paragraph'."
     Output: {{"tool_choice": "summarise_text", "tool_input": "'long paragraph'"}}

5. no tool: Use for general conversation and questions
   - Example inputs and outputs:
     Input: "Who are you?"
     Output: {{"tool_choice": "no tool", "tool_input": "I am an AI assistant that can help you with calculations, reverse text, and answer questions. I can perform mathematical operations and reverse strings. How can I help you today?"}}
     
     Input: "How are you?"
     Output: {{"tool_choice": "no tool", "tool_input": "I'm functioning well, thank you for asking! I'm here to help you with calculations, text reversal, or answer any questions you might have."}}

STRICT RULES:
1. For questions about identity, capabilities, feelings, and general questions:
   - ALWAYS use `no tool`
   - ALWAYS provide a complete, friendly response
   - If user asks a question, ALWAYS answer it; do not simply repeat the question
   - ALWAYS keep your answers relevant to the user's query
   - If the user asks a question like 'What can you do?', ALWAYS mention your capabilities

2. For ANY text reversal request:
   - ALWAYS use `reverse_string`
   - Extract ONLY the text to be reversed
   - Provide the text as is to the reversal tool; do not modify it before sending it to `reverse_string`
   - Remove quotes, "reverse of", and other extra text

3. For ANY math operations:
   - ALWAYS use `basic_calculator`
   - Extract the numbers and operation
   - Convert text numbers to digits

4. For ANY timer requests:
   - ALWAYS use `timer`
   - Extract the duration in seconds
   - Ensure the duration is a valid number
   - If the duration is not provided, tell the user to try again; DO NOT set a timer

5. For ANY text summarization requests:
   - ALWAYS use `summarise_text`
   - If the user requests a summary, ALWAYS delegate the task to the `summarise_text` tool; DO NOT summarize the text yourself
   - DO NOT modify the text given in the prompt before sending it to `summarise_text`
   - Use the entire text given in the prompt as the input to `summarise_text`; DO NOT pass your own summary
   - STRICTLY follow the input format for the `summarise_text` tool

Here is a list of your tools along with their descriptions:
{tool_descriptions}

Remember: Your response must ALWAYS be valid JSON with "tool_choice" and "tool_input" fields.
"""

class Agent:
    def __init__(self, tools, model_service, model_name, stop = None):
        """
        Initializes the agent with a list of tools and a model.
        """
        self.tools = tools
        self.model_service = model_service
        self.model_name = model_name
        self.stop = stop
        print("[agent]: Agent initialized with model:", model_name)

    def prepare_tools(self):
        """
        Stores the tools in the toolbox and returns their descriptions.
        """
        toolbox = ToolBox()
        toolbox.store(self.tools)
        tool_descriptions = toolbox.tools()
        return tool_descriptions

    async def think(self, prompt):
        """
        Runs the generate_text method on the model using the system prompt template and tool descriptions.
        """
        tool_descriptions = self.prepare_tools()
        agent_system_prompt = system_prompt_template.format(tool_descriptions = tool_descriptions)

        # create an instance of the model service with the system prompt
        model_instance = self.model_service(
            model = self.model_name,
            system_prompt = agent_system_prompt,
            temperature = 0.2,
            stop = self.stop
        )

        # generate and return the response dictionary
        print("[agent]: Thinking...\n")
        agent_response_dict = await model_instance.generate_text(prompt)
        return agent_response_dict

    async def work(self, prompt):
        """
        Parses the dictionary returned from think and executes the appropriate tool.
        """
        agent_response_dict = await self.think(prompt)
        tool_choice = agent_response_dict.get("tool_choice")
        tool_input = agent_response_dict.get("tool_input")

        if tool_choice == "summarise_text":
                response = await summarise_text(prompt)
                # response = f"Here're two summaries for you!\n1. Prepared by the summarizer - {response}\n2. Prepared by LLM ({self.model_name}) - {str(tool_input)}"
                print(f"[agent]: {colored(response, 'cyan')}")
                return f"{response}"  # for streamlit app

        for tool in self.tools:
            if tool.__name__ == tool_choice:
                response = await tool(tool_input)  # make sure tool function is async
                print(f"[agent]: {colored(response, 'cyan')}")
                return f"{response}"  # for streamlit app

        print(f"[agent]: {colored(tool_input, 'cyan')}\n")
        return f"{tool_input}" # for streamlit app
    
    # example usage
if __name__ == "__main__":
    """
    Instructions for using this agent:
    
    Example queries you can try:
    1. Calculator operations:
       - "Calculate 15 plus 7"
       - "What is 100 divided by 5?"
       - "Multiply 23 and 4"
    
    2. String reversal:
       - "Reverse the word 'hello world'"
       - "Can you reverse 'Python Programming'?"
    
    3. Timer:
       - "Set a timer for 10 seconds"
       - "Timer for 60 seconds"

    4. Text summarization:
       - "Summarize the text: 'This is a long text that needs to be summarized.'"
       - "Can you summarize this paragraph?"
    
    5. General questions (will get direct responses):
       - "Who are you?"
       - "What can you help me with?"
    """

    tools = [basic_calculator, reverse_string, timer, summarise_text]

    # using ollama with llama3.2-3b model
    model_service = OllamaModel
    model_name = "llama3.2:3b"  
    stop = "<|eot_id|>"

    agent = Agent(tools = tools, model_service = model_service, model_name = model_name, stop = stop)

    print("\n[agent] : Hello, I'm your AI Assistant!")
    print("You can ask me to:")
    print("    1. Perform calculations (e.g., 'Calculate 15 plus 7')")
    print("    2. Reverse strings (e.g., 'Reverse hello world')")
    print("    3. Set a timer (e.g., 'Set a timer for 10 seconds')")
    print("    4. Summarize text (e.g., 'Summarize the text: This is a long text')")
    print("    5. Answer general questions (e.g., 'What day comes after Sunday?')")
    print("Type 'exit' to end the conversation.\n")

    while True:
        prompt = input("[agent]: Ask me anything: ")
        if prompt.lower() == "exit":
            break

        asyncio.run(agent.work(prompt))