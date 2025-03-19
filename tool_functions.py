import json, operator, time, asyncio
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("Falconsai/text_summarization") # loading tokenizer
model = AutoModelForSeq2SeqLM.from_pretrained("Falconsai/text_summarization") # loading model

async def basic_calculator(input_str):
    """
    Perform a numeric operation on two numbers based on the input string or dictionary.

    Parameters:
    input_str (str or dict): Either a JSON string representing a dictionary with keys 'num1', 'num2', and 'operation',
                            or a dictionary directly. Example: '{"num1": 5, "num2": 3, "operation": "add"}'
                            or {"num1": 67869, "num2": 9030393, "operation": "divide"}

    Returns:
    str: The formatted result of the operation.

    Raises:
    Exception: If an error occurs during the operation (e.g., division by zero).
    ValueError: If an unsupported operation is requested or input is invalid.
    """
    try:
        # handle both dictionary and string inputs
        if isinstance(input_str, dict):
            input_dict = input_str
        else:
            # clean and parse the input string
            input_str_clean = input_str.replace("'", "\"")
            input_str_clean = input_str_clean.strip().strip("\"")
            input_dict = json.loads(input_str_clean)
        
        # validate required fields
        if not all(key in input_dict for key in ['num1', 'num2', 'operation']):
            return "Error: Input must contain 'num1', 'num2', and 'operation'.\n"

        num1 = float(input_dict['num1'])  # convert to float to handle decimal numbers
        num2 = float(input_dict['num2'])
        print(f"[calculator]: num1: {num1}, num2: {num2}")

        operation = input_dict['operation'].lower()
        print(f"[calculator]: operation: {operation}")  # make case-insensitive
    except (json.JSONDecodeError, KeyError) as e:
        return "Invalid input format. Please provide valid numbers and operation.\n"
    except ValueError as e:
        return "Error: Please provide valid numerical values.\n"

    # define the supported operations with error handling
    operations = {
        'add': operator.add, # + 
        'plus': operator.add, # + 
        'subtract': operator.sub, # -
        'minus': operator.sub,  # -
        'multiply': operator.mul, # *
        'times': operator.mul,  # *
        'divide': operator.truediv, # /
        'floor_divide': operator.floordiv, # //
        'modulus': operator.mod, # %
        'power': operator.pow, # **
        'lt': operator.lt, # <
        'le': operator.le, # <=
        'eq': operator.eq, # ==
        'ne': operator.ne, # != 
        'ge': operator.ge, # >=
        'gt': operator.gt # >
    }

    # check if the operation is supported
    if operation not in operations:
        return f"[error]: Unsupported operation: '{operation}'. Supported operations are: {', '.join(operations.keys())}.\n"

    try:
        # special handling for division by zero
        if (operation in ['divide', 'floor_divide', 'modulus']) and num2 == 0:
            return "[error]: Division by zero is not allowed.\n"

        # perform the operation
        result = operations[operation](num1, num2)
        
        # format result based on type
        if isinstance(result, bool):
            result_str = "True" if result else "False"
        elif isinstance(result, float):
            # handle floating point precision
            result_str = f"{result:.6f}".rstrip('0').rstrip('.')
        else:
            result_str = str(result)

        return f"[calculator]: The answer is: {result_str}.\n"
    except Exception as e:
        return f"[error]: Error during calculation: {str(e)}.\n"

async def reverse_string(input_str):
    """
    Reverse the given string.

    Parameters:
    input_str (str): The string to be reversed.

    Returns:
    str: The reversed string.
    """
    # check if input is a string
    if not isinstance(input_str, str):
        return "[error]: Input must be a string\n"
    
    print(f"[string-reverser]: Input string: '{input_str}'.")
    
    # reverse the string using slicing
    reversed_string = input_str[::-1]
    
    # format the output
    result = f"[string-reverser]: The reversed string is: '{reversed_string}'.\n"
    
    return result

async def timer(input_str):
    """
    Timer function to set a timer for a specified duration.

    Parameters:
    input_str (str): The duration of the timer in seconds.

    Returns:
    str: A message indicating the timer has expired after the set-timer expires.
    """
    # check if input is a string
    if not isinstance(input_str, str):
        return "[error]: Input must be a string.\n"
    
    # convert the input to an integer
    try:
        duration = int(input_str)
    except ValueError:
        return "[error]: Invalid duration. Please provide a valid number of seconds.\n"

    # setting timer
    i = duration
    while i > 0:
        if i == duration:
            print(f"[timer]: Setting timer for {duration} seconds...")
        elif i == duration - 1:
            print(f"{i} seconds remaining...")
        elif i > 10:
            if i % 5 == 0:
                print(i)
                i -= 5
                time.sleep(5)
                continue
        else:
            print(i)
        time.sleep(1)
        i -= 1
        
    return f"[timer]: Timer for {duration} seconds has expired!\n"

async def summarise_text(input_str):
    """
    Text summarising function to generate concise and meaningful summaries of the input text.

    Parameters:
    input_str (str): The text that needs to be summarized.

    Returns:
    str: A summary of the input text.
    """
    # check if input is a string
    if not isinstance(input_str, str):
        return "[error]: Input must be a string.\n"
    
    # prepare input
    inputs = await asyncio.to_thread(tokenizer,
            f"summarize: {input_str}", 
            max_length = 512, 
            return_tensors = "pt", 
            truncation = True)
    
    # generate summary
    summary_ids = await asyncio.to_thread(model.generate,
        inputs.input_ids, 
        num_beams = 4, 
        max_length = 100, 
        early_stopping = True)
    
    # decode summary
    summary = await asyncio.to_thread(tokenizer.decode,
        summary_ids[0], 
        skip_special_tokens = True)

    # # using the Hugging Face pipeline for summarization
    # summarizer = pipeline("summarization", model = "Falconsai/text_summarization")
    # # summarizer = pipeline("summarization", model = "sshleifer/distilbart-cnn-12-6")
    # summary = await asyncio.to_thread(summarizer, input_str, max_length = 100, min_length = 20, do_sample = False)

    print(f"[summarizer]: Input text: '{input_str}'")

    # return f"[summarizer]: {summary[0]['summary_text']}\n"
    return f"[summarizer]: {summary}\n"