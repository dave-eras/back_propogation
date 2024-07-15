import streamlit as st
import pandas as pd
import numpy as np

# Function to load data
@st.cache_resource
def load_data(file_path):
    return pd.read_excel(file_path)

# Function to update ability level
def update_level(x_i, y_i, q_i, beta_i, lambda_i):
    pi_i = 1 / (1 + np.exp(-beta_i * (x_i - q_i)))
    x_i_1 = x_i + lambda_i * (y_i - pi_i)
    return x_i_1

# Function to select the initial question
def select_initial_question(df):
    # Initial pool of easier questions, adjust the value if needed
    question_pool = df[df['estimated level/18'] < 4]
    
    if not question_pool.empty:
        return question_pool.sample(1).iloc[0]
    else:
        return None

# Simplified function to select the next question based on the current level
def select_next_question(df, current_level, seen_questions):
    eligible_questions = df[~df.index.isin(seen_questions)]
    # Find the question with q_i closest to x_i
    if not eligible_questions.empty:
        eligible_questions['distance'] = np.abs(eligible_questions['estimated level/18'] - current_level)
        closest_question_idx = eligible_questions['distance'].idxmin()
        return df.loc[closest_question_idx], closest_question_idx
    else:
        return None, None

# Function to calculate the decayed learning rate
def calculate_decay_learning_rate(initial_lambda, min_lambda, total_questions, questions_answered):
    decay = (initial_lambda - min_lambda) / total_questions
    decayed_lambda = max(initial_lambda - decay * questions_answered, min_lambda)
    return decayed_lambda

# Path to the Excel file
file_path = 'C:\\Users\\dmitc\\back_prop\\Lib\\data_for_back_propagation.xlsx'

# Load data
df = load_data(file_path)

# Parameters for learning rate decay
initial_lambda = 2.5  # Initial learning rate
min_lambda = 1      # Minimum learning rate
total_questions = 20  # Total number of questions in the test

# Initialize session state
if 'seen_questions' not in st.session_state:
    st.session_state.seen_questions = []
    st.session_state.questions_answered = 0
    st.session_state.initial_ability_set = True
    st.session_state.current_level = 1.2   # Start ability level at 1.3 on the 18-point scale

    # Select the initial question based on the initial ability level
    st.session_state.selected_question = select_initial_question(df)
    if st.session_state.selected_question is not None:
        st.session_state.selected_question_idx = st.session_state.selected_question.name
        st.session_state.seen_questions.append(st.session_state.selected_question_idx)
    else:
        st.write("No more questions available.")
        st.stop()

selected_question = st.session_state.selected_question

# Display question number
st.write(f"Question {st.session_state.questions_answered + 1}/{total_questions}")

# Display instructions
st.write(f"**Instruction**: {selected_question['instruct']}")

# Optionally display input text
if pd.notna(selected_question['rclctext']):
    st.write(f"**Input Text**: {selected_question['rclctext']}")

# Optionally display question
if pd.notna(selected_question['question']):
    st.write(f"**Question**: {selected_question['question']}")

# Fetch the text for 'correct' and 'incorrect' responses
correct_text = selected_question['correct']
incorrect_text = selected_question['incorrect']

# Simulate a response
response = st.radio('Response:', [f'Correct ({correct_text})', f'Incorrect ({incorrect_text})'])
y_i = 1 if 'Correct' in response else 0

# Add submit button
submit_button = st.button('Submit')

# Add placeholders for message, question difficulty level, learning rate, and current ability level
message_placeholder = st.empty()
q_i_placeholder = st.empty()
decayed_lambda_placeholder = st.empty()
x_i_placeholder = st.empty()

# Display question difficulty level
q_i = selected_question['estimated level/18']  # Difficulty Level
beta_i = selected_question['beta']  # Beta Value
q_i_placeholder.write(f"**Question Difficulty Level (q_i)**: {q_i}")

# Calculate the current decayed learning rate
decayed_lambda = calculate_decay_learning_rate(initial_lambda, min_lambda, total_questions, st.session_state.questions_answered)
decayed_lambda_placeholder.write(f"**Current Learning Rate (λ)**: {decayed_lambda}")

# Display current ability level (x_i)
x_i = st.session_state.current_level
x_i_placeholder.write(f"**Current Ability Level (x_i)**: {x_i}")

# Update ability level and select the next question if submit button is clicked
if submit_button:
    st.session_state.current_level = update_level(x_i, y_i, q_i, beta_i, decayed_lambda)
    st.session_state.questions_answered += 1

    # Check if the current ability level hits -1.5 or below
    if st.session_state.current_level <= -1.2:
        message_placeholder.write("BEGINNERS' COURSE FOR YOU")
        st.stop()
    
    # Check if 20 questions have been answered
    if st.session_state.questions_answered >= total_questions:
        x_i_final = st.session_state.current_level
        
        if 0 <= x_i_final < 4:
            message_placeholder.write("A1 LEVEL FOR YOU")
        elif 4 <= x_i_final < 7:
            message_placeholder.write("A2 LEVEL FOR YOU")
        elif 7 <= x_i_final < 10:
            message_placeholder.write("B1 LEVEL FOR YOU")
        elif 10 <= x_i_final < 13:
            message_placeholder.write("B2 LEVEL FOR YOU")
        elif 13 <= x_i_final < 16:
            message_placeholder.write("YOU ARE C1 - WE DON'T HAVE THAT")
        elif x_i_final >= 16:
            message_placeholder.write("YOU ARE C2 - WE DON'T HAVE THAT")
        
        st.stop()
    
    next_question, next_question_idx = select_next_question(df, st.session_state.current_level, st.session_state.seen_questions)
    
    if next_question is not None:
        st.session_state.selected_question = next_question
        st.session_state.selected_question_idx = next_question_idx
        st.session_state.seen_questions.append(next_question_idx)
    else:
        st.write("No more questions available.")
        st.stop()
    
    st.rerun()

# Display remaining elements
q_i_placeholder.write(f"**Question Difficulty Level (q_i)**: {q_i}")
decayed_lambda_placeholder.write(f"**Current Learning Rate (λ)**: {decayed_lambda}")
x_i_placeholder.write(f"**Current Ability Level (x_i)**: {st.session_state.current_level}")