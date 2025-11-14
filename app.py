import streamlit as st
import requests

BASE_URL= "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Web Chatbot", layout="wide")
st.title("Smart Web Chatbot")

tabs = st.tabs(["Normal Chatbot", "Business Assistant"])

with tabs[0]:
  st.subheader("Chat with assistant")
  if 'normal_history' not in st.session_state:
    st.session_state.normal_history = []

  user_input = st.text_input("Your message:", key="normal_input")
  answer = ""
  if st.button("Send", key="normal_send"):
    if user_input.strip():
      prompt = user_input
      payload = {"user_id": "normal_user", "question": prompt}
      try:
        res = requests.post(f"{BASE_URL}/ask", json=payload)
        if res.status_code == 200:
          answer = res.json().get("answer", "No answer found.")
        else:
          answer = f"Error: {res.text}"
      except Exception as e:
        answer = f"Error: {str(e)}"

      st.session_state.normal_history.append({"user": user_input, "bot": answer})

  for chat in st.session_state.normal_history:
    st.markdown(f"**You:** {chat['user']}")
    st.markdown(f"**Bot:** {chat['bot']}")

with tabs[1]:
  st.subheader("Chat with a business Assistant")
  if 'business_history' not in st.session_state:
    st.session_state.business_history = {}

  col1, col2, col3 = st.columns([3,3,1])
  with col1:
    company_name = st.text_input("Company Name:", key="company_name")
  with col2:
    company_url = st.text_input("Company Website URL:", key="company_url")
  with col3:
    user_id = st.text_input("User ID:", key="business_user_id")

  if st.button("Scrape and create assistant"):
    if company_name and company_url and user_id:
      payload = {
        "user_id": user_id,
        "company_name": company_name,
        "company_url": company_url
      }
      try:
        res = requests.post(f"{BASE_URL}/scrape", json=payload)
        if res.status_code == 200:
          st.success("Assitant ready. You can now ask questions.")
          if user_id not in st.session_state.business_history:
            st.session_state.business_history[user_id] = []
        else:
          st.error(f"Scraping failed: {res.text}")
      except Exception as e:
        st.error(f"Error: {str(e)}")

  if user_id in st.session_state.business_history:
    user_msg = st.text_input("Your question:", key=f"ask_{user_id}")
    answer = ""
    if st.button("Send", key=f"send_{user_id}"):
      if user_msg.strip():
        payload = {"user_id": user_id, "question": user_msg}
        try:
          res = requests.post(f"{BASE_URL}/ask", json=payload)
          if res.status_code == 200:
            data = res.json()
            answer = data.get("answer", "No answer found.")
          else:
            answer = f"Error: {res.text}"
        except Exception as e:
          answer = f"Error: {str(e)}"

        st.session_state.business_history[user_id].append({"user": user_msg, "bot": answer})

    for chat in st.session_state.business_history[user_id]:
      st.markdown(f"**You** {chat['user']}")
      st.markdown(f"**Bot** {chat['bot']}")