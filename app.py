# app.py
import streamlit as st
import pandas as pd
from login import login_user
from recommend import show_recommendations

# 데이터 로드
user_df = pd.read_csv('sample_user.csv')

# 로그인 페이지
def login_page():
    st.title("로그인 페이지")
    account_id = st.text_input("Account ID")

    if st.button("로그인"):
        user = login_user(account_id, user_df)

        if user is not None:
            st.session_state['user'] = user
            st.session_state['logged_in'] = True  # 로그인 상태
            st.experimental_rerun()  # 페이지 새로 고침
        else:
            st.error("로그인 실패: 잘못된 Account ID입니다.")

# 추천 페이지
def recommend_page():
    if 'user' in st.session_state:
        st.success(f"{st.session_state['user']['ACCOUNT_ID']}님 환영합니다!")
        show_recommendations()  # 추천 영화 함수 호출
    else:
        st.error("로그인 후 추천 영화를 확인하세요.")

# 페이지 전환 처리
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    recommend_page()
else:
    login_page()
