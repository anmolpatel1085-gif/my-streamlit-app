try:
    import streamlit as st
    print('streamlit', st.__version__)
except Exception as e:
    print('error', e)
    raise
