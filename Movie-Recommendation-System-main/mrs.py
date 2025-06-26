import streamlit as st
import pickle
import pandas as pd
import requests
import gzip
from urllib.parse import quote

# ✅ OMDB API Key
OMDB_API_KEY = 'c1089238'

# 🌙 Dark Mode Styling
st.markdown("""
    <style>
        body {
            background-color: #111;
            color: white;
        }
        .stButton>button {
            background-color: #444;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ Load movie data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# ✅ Load compressed similarity file
with gzip.open("similarity.pkl.gz", "rb") as f:
    similarity = pickle.load(f)

# ✅ Ensure 'genres' column exists
if 'genres' not in movies.columns:
    st.warning("⚠️ 'genres' column not found in your dataset. Genre filter disabled.")
    movies['genres'] = "Unknown"

# ✅ Fetch movie details from OMDB
def fetch_movie_details(title):
    try:
        safe_title = quote(title)
        url = f"https://www.omdbapi.com/?t={safe_title}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data.get('Response') == 'True':
            poster = data.get('Poster', '')
            if poster == 'N/A' or not poster:
                poster = "https://via.placeholder.com/300x450?text=No+Image"
            return {
                'poster': poster,
                'plot': data.get('Plot', 'No plot available'),
                'rating': data.get('imdbRating', 'N/A'),
                'genre': data.get('Genre', 'N/A'),
                'actors': data.get('Actors', 'N/A'),
                'director': data.get('Director', 'N/A'),
                'runtime': data.get('Runtime', 'N/A')
            }
    except Exception as e:
        print(f"❌ Error fetching details for '{title}':", e)
    return {
        'poster': "https://via.placeholder.com/300x450?text=No+Image",
        'plot': 'No plot available',
        'rating': 'N/A',
        'genre': 'N/A',
        'actors': 'N/A',
        'director': 'N/A',
        'runtime': 'N/A'
    }

# ✅ Recommend similar movies
def recommend(movie_title):
    movie_index = movies[movies['title'] == movie_title].index[0]
    distances = similarity[movie_index]
    similar_movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_data = []
    for rec_idx in similar_movies:
        rec_title = movies.iloc[rec_idx[0]].title
        details = fetch_movie_details(rec_title)
        recommended_data.append({
            'title': rec_title,
            'poster': details['poster'],
            'plot': details['plot'],
            'rating': details['rating'],
            'genre': details['genre'],
            'actors': details['actors'],
            'director': details['director'],
            'runtime': details['runtime']
        })
    return recommended_data

# ✅ Genre filter
unique_genres = sorted(set(
    g.strip() for sub in movies['genres'] if isinstance(sub, str) for g in sub.split(', ')
))
selected_genre = st.selectbox("🎭 Filter by Genre:", ["All"] + unique_genres)

filtered_titles = movies['title']
if selected_genre != "All":
    filtered_titles = movies[movies['genres'].str.contains(selected_genre, na=False)]['title']

# ✅ UI Title
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    filtered_titles)

# ✅ Show recommendations
if st.button('Recommend'):
    recommendations = recommend(selected_movie_name)
    if not recommendations:
        st.error("No recommendations found.")
    else:
        favorites = []
        for i, rec in enumerate(recommendations):
            unique_key = f"{rec['title']}_{i}"

            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(rec['poster'], width=180, caption=rec['title'])
            with col2:
                st.markdown(f"**Genre:** {rec['genre']}")
                st.markdown(f"**IMDb Rating:** ⭐ {rec['rating']}")
                st.markdown(f"**Cast:** 🎭 {rec['actors']}")
                st.markdown(f"**Director:** 🎬 {rec['director']}")
                st.markdown(f"**Runtime:** ⏱ {rec['runtime']}")
                st.markdown(f"**Overview:** {rec['plot']}")
                # ▶️ YouTube Trailer Button
                yt_url = f"https://www.youtube.com/results?search_query={quote(rec['title'] + ' official trailer')}"
                st.markdown(f"[▶️ Watch Trailer]({yt_url})", unsafe_allow_html=True)
                # ⭐ User Rating
                rating = st.slider(f"Rate **{rec['title']}**:", 1, 5, key=f"{unique_key}_rating")
                st.text(f"Your rating: {rating}/5")
                # ❤️ Favorite Selection
                if st.checkbox(f"Add to favorites: {rec['title']}", key=f"{unique_key}_fav"):
                    favorites.append(rec['title'])

            st.markdown("---")

        # ✅ Save favorites to CSV
        if favorites:
            df = pd.DataFrame(favorites, columns=["Favorite Movies"])
            st.download_button("📥 Download Favorites", df.to_csv(index=False), file_name="favorites.csv",
                               mime="text/csv")
