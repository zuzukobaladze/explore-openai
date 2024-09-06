import streamlit as st


# Mock function to simulate backend API call
def get_bot_response(user_input):
    # Replace this with your actual backend API endpoint
    api_url = "http://your-backend-api-endpoint/chat"
    # Simulating a POST request with user input
    try:
        # Uncomment below when using a real API
        # response = requests.post(api_url, json={"message": user_input})
        # bot_message = response.json().get("bot_message", "Sorry, I couldn't understand that.")

        # Mock response for the example
        bot_message = f"Simulated response for: {user_input}"
        return bot_message
    except Exception as e:
        return f"Error: {str(e)}"


# Initialize session state to store the chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""


# Function to display chat messages
def display_chat():
    for msg in st.session_state.messages:
        if msg["user"] == "You":
            st.markdown(
                f"<div style='text-align: right;'><strong>{msg['user']}:</strong> {msg['text']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='text-align: left;'><strong>{msg['user']}:</strong> {msg['text']}</div>",
                unsafe_allow_html=True,
            )


# Main chat display
st.title("Chat Application")
st.write("Chat with the bot below:")

# Display the chat
display_chat()

# Chat input prompt box at the bottom
user_input = st.text_input("Type your message here and press Enter", key="input_text")

# Check if there is any new user input
if st.button("Send"):
    if user_input:
        # Append the user input to the session state
        st.session_state.messages.append({"user": "You", "text": user_input})

        # Call the backend to get the bot's response
        bot_response = get_bot_response(user_input)
        st.session_state.messages.append({"user": "Bot", "text": bot_response})

        # Reset the input text field after sending the message
        st.session_state.input_text = ""  # Clear the session state
        st.rerun()  # Rerun the app to clear the input box
    else:
        st.warning("Please enter a message before sending.")
