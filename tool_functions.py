import json, operator, time

def basic_calculator(input_str):
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
            return "Error: Input must contain 'num1', 'num2', and 'operation'"

        num1 = float(input_dict['num1'])  # convert to float to handle decimal numbers
        num2 = float(input_dict['num2'])
        operation = input_dict['operation'].lower()  # make case-insensitive
    except (json.JSONDecodeError, KeyError) as e:
        return "Invalid input format. Please provide valid numbers and operation."
    except ValueError as e:
        return "Error: Please provide valid numerical values."

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
        return f"[error]: Unsupported operation: '{operation}'. Supported operations are: {', '.join(operations.keys())}"

    try:
        # special handling for division by zero
        if (operation in ['divide', 'floor_divide', 'modulus']) and num2 == 0:
            return "[error]: Division by zero is not allowed"

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

        return f"[calculator]: The answer is: {result_str}"
    except Exception as e:
        return f"[error]: Error during calculation: {str(e)}"

def reverse_string(input_string):
    """
    Reverse the given string.

    Parameters:
    input_string (str): The string to be reversed.

    Returns:
    str: The reversed string.
    """
    # check if input is a string
    if not isinstance(input_string, str):
        return "[error]: Input must be a string"
    
    # reverse the string using slicing
    reversed_string = input_string[::-1]
    
    # format the output
    result = f"[string-reverser]: The reversed string is: {reversed_string}"
    
    return result

def timer(input_string):
    """
    Timer function to set a timer for a specified duration.

    Parameters:
    input_string (str): The duration of the timer in seconds.

    Returns:
    str: A message indicating the timer has expired after the set-timer expires.
    """
    # check if input is a string
    if not isinstance(input_string, str):
        return "[error]: Input must be a string"
    
    # convert the input to an integer
    try:
        duration = int(input_string)
    except ValueError:
        return "[error]: Invalid duration. Please provide a valid number of seconds."

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
        
    return f"[timer]: Timer for {duration} seconds has expired!"