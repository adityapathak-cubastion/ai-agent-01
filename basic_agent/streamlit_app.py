import streamlit as st, asyncio
from tool_functions import basic_calculator, reverse_string, timer, summarise_text
from agent import OllamaModel, Agent  # import the relevant classes

# initialize the tools and model as in your original script
tools = [basic_calculator, reverse_string, timer, summarise_text]
model_service = OllamaModel
model_name = "llama3.2:3b"  
stop = "<|eot_id|>"

# initialize the agent
# agent = Agent(tools = tools, model_service = model_service, model_name = model_name, stop = stop)

# streamlit interface
def main():
    agent = Agent(tools = tools, model_service = model_service, model_name = model_name, stop = stop) # agent initialized

    st.title("AI Agent 01")
    st.write("\n**[agent]:** Hello, I'm your AI Assistant!")
    st.write("You can ask me to:")
    st.write("    1. Perform calculations (e.g., 'Calculate 15 plus 7')")
    st.write("    2. Reverse strings (e.g., 'Reverse hello world')")
    st.write("    3. Set a timer (e.g., 'Set a timer for 10 seconds')")
    st.write("    4. Summarize text (e.g., 'Summarize the text: This is a long text')")
    st.write("    5. Answer general questions (e.g., 'What day comes after Sunday?')")
    
    user_input = st.text_input("**[me]:**", "")
    
    if st.button("Submit") and user_input:
        # display loading message while processing
        with st.spinner("Thinking..."):
            response = asyncio.run(agent.work(user_input))  # running agent's work method to process the input
            if response:
                st.write(f"**[agent]:** {response}")
            else:
                st.write("I'm not sure how to answer that, please try again.")

if __name__ == "__main__":
    main()
