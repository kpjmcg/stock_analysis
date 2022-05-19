from cgi import test
import streamlit as st

radio =  st.radio('Options', ('a','b','c'))

def test_print(thing):
    st.write('You chose', thing)

if radio == 'a':
    test_print(radio)
elif radio == 'b':
    test_print(radio)
elif radio == 'c':
    test_print(radio)
else:
    st.write('no choice')