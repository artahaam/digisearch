import streamlit as st

from digisearch.rag.online_llm import get_rag_response


WELCOME_MESSAGE = {
    "role": "assistant",
    "content": "سلام! چطور می‌تونم کمکتون کنم؟",
}

if "messages" not in st.session_state:
    st.session_state.messages = [WELCOME_MESSAGE]

AVATARS = {"user": "🧑", "assistant": "🤖"}


with st.sidebar:
    st.header("گزینه‌ها")
    if st.button("🗑️ شروع گفتگوی جدید", use_container_width=True):
        st.session_state.messages = [WELCOME_MESSAGE]
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=AVATARS.get(message["role"])):
        st.markdown(message["content"])

prompt = st.chat_input("چه سوالی داری؟")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("🔎 در حال جستجو و آماده‌سازی پاسخ..."):
            # try:
            response = get_rag_response(prompt, 5
                                            #    , st.session_state.messages
                                               )
                
            # except Exception:
            #     response = (
            #         "⚠️ متاسفانه در پردازش درخواست شما مشکلی پیش اومد. "
            #         "لطفاً دوباره تلاش کنید یا سوال رو به شکل دیگه‌ای مطرح کنید."
            #     )

        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})