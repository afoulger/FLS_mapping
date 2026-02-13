import streamlit as st
import pandas as pd
import numpy as np
import time

st.title("My practice app")

df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
})

option = st.selectbox(
    'Choose a number',
    df['first column'])

'You chose: ', option

my_dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))
st.dataframe(my_dataframe.style.highlight_max(axis=0))
#st.table(my_dataframe.style.highlight_max(axis=0))

chart_data = pd.DataFrame(
    np.random.randn(100, 6),
    columns=['a', 'b', 'c', 'd', 'e', 'f'])

st.line_chart(chart_data)


if st.checkbox('Show map'):
    map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [10, 10] + [55.68, 12.57],
        columns=['lat', 'lon'])

    st.map(map_data)




x = st.slider('x')  #this is a widget
st.write(x, 'squared is', x * x)



st.text_input("Your name", key="name2")

# You can access the value at any point with:
st.session_state.name2


# Add some text
st.write("Welcome to my simple app. Enter your name below!")
 
# Create a text input box
name = st.text_input("What is your name?", key= "name")
 
# Create a button
if st.button("Say Hello"):
    if name:
        st.success(f"Hello, {name}! This app is running live.")
    else:
        st.warning("Please enter a name first.")
 
# Add a slider for fun
age = st.slider("Select your age", 0, 100, 25)
st.write(f"You are {age} years old.")

st.session_state.name


if st.checkbox('Show dataframe'):
    chart_data2 = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    chart_data2

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

# Add a slider to the sidebar:
add_slider = st.sidebar.slider(
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0)
)

left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
with left_column:
    if st.button('Press me!'):
        st.success("Hello, you have pressed the button!")

# Or even better, call Streamlit functions inside a "with" block:
with right_column:
    chosen = st.radio(
        'Sorting hat',
        ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
    st.write(f"You are in {chosen} house!")




'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

'...and now we\'re done!'