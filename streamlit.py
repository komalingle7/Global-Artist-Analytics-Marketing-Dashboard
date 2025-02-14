import streamlit as st
import main
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
st.set_page_config(page_title="Artist Analytics", layout="wide")

# User Input
artist_name = st.sidebar.text_input("Enter Artist Name", "SUGA")

# Initialize Analytics
analytics = main.ArtistAnalytics(artist_name)

# Dashboard Header
st.title("Artist Analytics Dashboard")
st.header("Real-time Multi-Platform Performance Analysis")
st.header(f"{artist_name}'s profile")

# Quick Metrics
col1, col2, col3= st.columns(3)
with col1:
    spotify_followers = analytics.spotify_artist.get('followers', {}).get('total', 0)
    st.metric("Spotify Followers", f"{spotify_followers:,}")
# with col2:
#     yt_stats = analytics.get_youtube_analytics()
#     yt_subs = yt_stats.get('subscriberCount', 'N/A') if yt_stats else 'N/A'
#     st.metric("YouTube Subscribers", f"{yt_subs:,}")
with col2:
    yt_stats = analytics.get_youtube_analytics()
    yt_subs = int(yt_stats.get("subscriberCount", 0)) if yt_stats else 0
    st.metric("YouTube Subscribers", yt_subs)
with col3:
    events = analytics.get_ticketmaster_events()
    upcoming_events = len(events) if not events.empty else 0
    st.metric("Upcoming Events", upcoming_events)
# Main Tabs
tab1, tab2, tab3, tab4, tab5= st.tabs([
    "Overview", "Music", "Social", "Events", "Trends"
])

with tab1:
    st.header("Cross-Platform Overview")
    col1, col2 = st.columns(2)

    # with col1:
    #     st.subheader("Spotify Popularity Trajectory")
    #     spotify_data = analytics.get_spotify_data()
    #     fig = px.bar(spotify_data, x='release_date', y='popularity',
    #                   title="Track Popularity Over Time")
    #     st.plotly_chart(fig, use_container_width=True)
    with col1:
        st.subheader("Spotify Popularity Distribution")
        spotify_data = analytics.get_spotify_data()

        fig = px.pie(spotify_data, names='release_date', values='popularity',
                     title="Track Popularity Distribution")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("YouTube Engagement")
        if yt_stats:
            yt_metrics = pd.DataFrame({
                'Metric': ['Views', 'Subscribers', 'Videos'],
                'Count': [
                    int(yt_stats['viewCount']),
                    int(yt_stats['subscriberCount']),
                    int(yt_stats['videoCount'])
                ]
            })
            fig = px.bar(yt_metrics, x='Metric', y='Count',
                         title="Channel Statistics")
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Music Analytics")
    col1, col2 = st.columns(2)

    # with col1:
    #     st.subheader("Top Tracks")
    #     fig = px.bar(spotify_data.sort_values('popularity', ascending=False).head(5),
    #                  x='name', y='popularity',
    #                  title="Most Popular Tracks")
    #     st.plotly_chart(fig, use_container_width=True)
    with col1:
        st.subheader("Top Tracks")

        # Sorting and selecting top 5 tracks based on popularity
        top_tracks = spotify_data.sort_values('popularity', ascending=False).head(5)

        # Creating a bubble chart
        fig = px.scatter(top_tracks, x='name', y='popularity', size='popularity',
                         color='name', title="Most Popular Tracks",
                         hover_data=['popularity'])

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Track Duration Distribution")
        fig = px.box(spotify_data, y='duration_ms',
                     title="Track Length Analysis")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Social Sentiment Analysis")
    reddit_data = analytics.get_reddit_sentiment()

    if not reddit_data.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sentiment Distribution")
            fig = px.histogram(reddit_data, x='sentiment', nbins=20,
                               title="Comment Sentiment Scores")
            st.plotly_chart(fig, use_container_width=True)

    #     with col2:
    #         st.subheader("Top Engaged Posts")
    #         top_posts = reddit_data.nlargest(10, 'score')
    #         fig = px.bar(top_posts, x='created', y='score',
    #                      title="Most Upvoted Comments")
    #         st.plotly_chart(fig, use_container_width=True)
    # else:
    #     st.warning("No social data available for this artist")
    with col2:
        st.subheader("Top Engaged Posts")

        # Slider to control the number of top posts displayed
        num_posts = st.slider("Select number of top posts", min_value=1, max_value=20, value=10)

        top_posts = reddit_data.nlargest(num_posts, 'score')  # Dynamically selects top N posts

        fig = px.bar(top_posts, x='created', y='score',
                     title="Most Upvoted Comments")

        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Event Analytics")
    if not events.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Upcoming Events Schedule")
            fig = px.timeline(events, x_start='date', x_end='date', y='venue',
                              title="Event Timeline")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Geographical Distribution")
            city_counts = events['city'].value_counts().reset_index()
            fig = px.pie(city_counts, values='count', names='city',
                         title="Event Locations")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No upcoming events found")

with tab5:
    st.header("Market Trends")
    trends_data = analytics.get_google_trends()

    if not trends_data.empty:
        fig = px.area(trends_data, x='date', y=artist_name,
                      title="3-Month Search Interest Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Trend data not available")

st.sidebar.markdown("## Data Freshness")
st.sidebar.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")