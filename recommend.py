import streamlit as st
import pandas as pd
import os
import glob

# 탭 생성
tab1, tab2 = st.tabs(['추천 영화', '전체 영화'])

def get_best_matching_image(movie_name):
    image_files = glob.glob(os.path.join('poster', '*'))
    best_match = None
    best_match_length = 0

    for image_file in image_files:
        image_name = os.path.basename(image_file).split('.')[0]
        match_length = 0

        for i in range(min(len(movie_name), len(image_name))):
            if movie_name[i].lower() == image_name[i].lower():
                match_length += 1
            else:
                break

        if match_length > best_match_length:
            best_match_length = match_length
            best_match = image_file

    return best_match

def show_movie_details(movie):
    # 사이드바 내용 설정
    with st.sidebar:
        st.title(movie['MOVIE_NAME'])
        st.write("장르:", movie['GENRE_NAME'])
        st.write("국가:", movie['NTY_NAME'])

        user_rating = st.session_state.user_ratings.get(movie['MOVIE_ID'], None)
        st.write("내 평점:", user_rating if user_rating else "없음")

        # 평균 평점 및 총 평점 수 계산
        other_ratings = st.session_state.ratings[st.session_state.ratings['MOVIE_ID'] == movie['MOVIE_ID']]
        avg_rating = other_ratings[other_ratings['EVENT_TYPE'] == 'rating']['EVENT_VALUE'].mean()
        total_ratings = other_ratings[other_ratings['EVENT_TYPE'] == 'rating'].shape[0]
        
        # 평점과 좋아요 수 갱신
        st.write("평점 (전체): {:.2f} (총 {}개)".format(avg_rating, total_ratings))
        st.slider("평점 (0-5)", 0, 5, user_rating if user_rating else 0, key=f"user_rating_{movie['MOVIE_ID']}")

        movie_id = movie["MOVIE_ID"]
        like_count = st.session_state.ratings[st.session_state.ratings['MOVIE_ID'] == movie_id].loc[st.session_state.ratings['EVENT_TYPE'] == 'like'].shape[0]
        like_button_label = "좋아요" if movie_id not in st.session_state.liked_movies else "좋아요 취소"
        
        st.write("좋아요 수:", like_count)
        if st.button(like_button_label, key=f"like_button_{movie_id}"):
            if movie_id in st.session_state.liked_movies:
                st.session_state.liked_movies.remove(movie_id)
            else:
                st.session_state.liked_movies.add(movie_id)

def show_recommendations():
    st.title("추천 영화")

    # 세션 상태 확인 및 초기화
    if 'movies' not in st.session_state:
        st.session_state.movies = pd.read_csv('sample_mv.csv')

    if 'ratings' not in st.session_state:
        st.session_state.ratings = pd.read_csv('sample_action.csv')

    if 'liked_movies' not in st.session_state:
        st.session_state.liked_movies = set(st.session_state.ratings[st.session_state.ratings['EVENT_TYPE'] == 'like']['MOVIE_ID'].tolist())

    user_id = st.session_state['user']['USER_ID']
    user_ratings = st.session_state.ratings[(st.session_state.ratings['USER_ID'] == user_id) & (st.session_state.ratings['EVENT_TYPE'] == 'rating')]

    if 'user_ratings' not in st.session_state:
        st.session_state.user_ratings = {row['MOVIE_ID']: row['EVENT_VALUE'] for _, row in user_ratings.iterrows()}

    # 탭 1: 추천 영화 (정렬된 영화)
    with tab1:
        sorted_movies = st.session_state.movies.copy()
        sorted_movies['RATING'] = sorted_movies['MOVIE_ID'].apply(lambda x: st.session_state.ratings[(st.session_state.ratings['MOVIE_ID'] == x) & (st.session_state.ratings['EVENT_TYPE'] == 'rating')]['EVENT_VALUE'].mean())
        sorted_movies = sorted_movies.sort_values(by='RATING', ascending=False)

        movies_per_page = 15
        total_movies = len(sorted_movies)
        total_pages = (total_movies // movies_per_page) + (1 if total_movies % movies_per_page > 0 else 0)

        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

        page = st.session_state.current_page
        start_idx = (page - 1) * movies_per_page
        end_idx = start_idx + movies_per_page
        current_movies = sorted_movies.iloc[start_idx:end_idx]

        cols = st.columns(5)
        for idx, movie in current_movies.iterrows():
            with cols[idx % 5]:
                movie_image = get_best_matching_image(movie["MOVIE_NAME"])
                if movie_image:
                    st.image(movie_image, caption="", use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/150x210", caption="", use_column_width=True)

                if st.button(movie["MOVIE_NAME"], key=f'movie_sorted_{idx}'):  
                    show_movie_details(movie)

                st.markdown(f"<small>{movie['NTY_NAME']}, {movie['GENRE_NAME']}</small>", unsafe_allow_html=True)

        # 페이지네이션
        pagination = st.container()
        with pagination:
            start_page = max(1, page - 2)
            end_page = min(total_pages, start_page + 4)
            if start_page == 1:
                end_page = min(5, total_pages)
            if end_page == total_pages:
                start_page = max(1, end_page - 4)

            cols = st.columns(end_page - start_page + 1)
            for idx, p in enumerate(range(start_page, end_page + 1)):
                with cols[idx]:
                    if st.button(str(p), key=f'page_sorted_{p}'):
                        st.session_state.current_page = p

    # 탭 2: 전체 영화 (정렬되지 않은 영화)
    with tab2:
        st.title("전체 영화")
        current_movies = st.session_state.movies
        cols = st.columns(5)
        for idx, movie in current_movies.iterrows():
            with cols[idx % 5]:
                movie_image = get_best_matching_image(movie["MOVIE_NAME"])
                if movie_image:
                    st.image(movie_image, caption="", use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/150x210", caption="", use_column_width=True)

                if st.button(movie["MOVIE_NAME"], key=f'movie_unsorted_{idx}'):
                    show_movie_details(movie)

                st.markdown(f"<small>{movie['NTY_NAME']}, {movie['GENRE_NAME']}</small>", unsafe_allow_html=True)

# 메인 함수 호출
if __name__ == "__main__":
    show_recommendations()
