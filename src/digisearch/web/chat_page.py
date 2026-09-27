import streamlit as st

from digisearch.rag.online_llm import get_rag_response


WELCOME_MESSAGE = {
    "role": "assistant",
    "content": "سلام! چطور می‌تونم کمکتون کنم؟",
}

LABELS = {"user": "🧑 شما", "assistant": "🤖 پاسخ دستیار"}

ERROR_MESSAGE = (
    "⚠️ متاسفانه در پردازش درخواست شما مشکلی پیش اومد. "
    "لطفاً دوباره تلاش کنید یا سوال رو به شکل دیگه‌ای مطرح کنید."
)

MAX_HISTORY_MESSAGES = 5

if "messages" not in st.session_state:
    st.session_state.messages = [WELCOME_MESSAGE]

with st.sidebar:
    st.header("گزینه‌ها")
    if st.button("🗑️ شروع گفتگوی جدید", use_container_width=True):
        st.session_state.messages = [WELCOME_MESSAGE]
        st.rerun()


def render_bubble(role: str, content: str, msg_key) -> None:

    kind = "user" if role == "user" else "assistant"
    with st.container(key=f"bubble_{kind}_{msg_key}"):
        st.markdown(f'<div class="chat-role-label">{LABELS[kind]}</div>', unsafe_allow_html=True)
        st.markdown(content)


with st.container(key="chat_shell_history"):
    for i, message_obj in enumerate(st.session_state.messages):
        render_bubble(message_obj["role"], message_obj["content"], msg_key=f"h{i}")

prompt = st.chat_input("چه سوالی داری؟")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.container(key="chat_shell_active"):
        render_bubble("user", prompt, msg_key="live_user")

        with st.container(key="bubble_assistant_live"):
            st.markdown(f'<div class="chat-role-label">{LABELS["assistant"]}</div>', unsafe_allow_html=True)
            with st.spinner("🔎 در حال جستجو و آماده‌سازی پاسخ..."):
                history = st.session_state.messages[:-1][-MAX_HISTORY_MESSAGES:]
                try:
                    response = get_rag_response(prompt, 5, history)
                except Exception:
                    response = ERROR_MESSAGE
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})