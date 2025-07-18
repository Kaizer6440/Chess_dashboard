import streamlit as st
import pandas as pd
import plotly.express as px

# Configure Streamlit page
st.set_page_config(page_title="♟ Chess Games Dashboard", page_icon="♟", layout="wide")
st.title("♟ Chess Games Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("../data/chess_games_data.csv")
    df.drop(["Unnamed: 15", "moves"], axis=1, errors='ignore', inplace=True)
    df.set_index("game_id", inplace=True)
    return df

chess = load_data()

# Sidebar filters
st.sidebar.header("Filter Games")

rated_options = st.sidebar.multiselect("Select Rated Option:", [True, False], default=[True, False])
victory_options = st.sidebar.multiselect("Victory Status:", sorted(chess["victory_status"].dropna().unique()), default=sorted(chess["victory_status"].dropna().unique()))
time_increments = st.sidebar.multiselect("Time Increment:", sorted(chess["time_increment"].dropna().unique()), default=sorted(chess["time_increment"].dropna().unique()))
openings = st.sidebar.multiselect("Opening Name:", sorted(chess["opening_shortname"].dropna().unique()), default=sorted(chess["opening_shortname"].dropna().unique()))
players = st.sidebar.multiselect("Player ID (White or Black):", sorted(pd.concat([chess["white_id"], chess["black_id"]]).dropna().unique()))

# Apply filters
filtered = chess[
    (chess["rated"].isin(rated_options)) &
    (chess["victory_status"].isin(victory_options)) &
    (chess["time_increment"].isin(time_increments)) &
    (chess["opening_shortname"].isin(openings))
]

if players:
    filtered = filtered[(filtered["white_id"].isin(players)) | (filtered["black_id"].isin(players))]

# Show sample data
st.subheader("Filtered Data Sample")
st.dataframe(filtered.head())

# CSV download button
st.download_button("Download Filtered Data as CSV", filtered.to_csv().encode('utf-8'), "filtered_chess_data.csv", "text/csv")

# Metrics
num_games = len(filtered)
avg_turns = filtered["turns"].mean()
rated_pct = (filtered["rated"].sum() / num_games) * 100 if num_games > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Games", f"{num_games:,}")
col2.metric("Avg Turns", f"{avg_turns:.2f}")
col3.metric("Rated Games %", f"{rated_pct:.1f}%")

# --- Plot 1: Most Popular Openings ---
st.subheader("Top 10 Most Popular Chess Openings")
pop = filtered[["opening_shortname"]].value_counts().head(10).reset_index()
pop.columns = ["Opening", "Count"]
fig1 = px.bar(pop, x="Count", y="Opening", orientation="h", color="Count", color_continuous_scale="Magma")
fig1.update_layout(title="Top 10 Most Popular Chess Openings", yaxis=dict(autorange="reversed"))
fig1.update_layout(template="plotly_dark")
st.plotly_chart(fig1, use_container_width=True)

# --- Plot 2: Win Distribution ---
st.subheader("Game Outcome Distribution")
fig2 = px.histogram(filtered, x="winner", color="winner", title="Win Distribution by Player Color",
                    color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(fig2, use_container_width=True)

# --- Plot 3: Victory Status ---
st.subheader("Victory Status Breakdown")
fig3 = px.histogram(filtered, x="victory_status", color="victory_status", title="Victory Status Frequency",
                    color_discrete_sequence=px.colors.qualitative.Set2)
st.plotly_chart(fig3, use_container_width=True)

# --- Plot 4: Rated vs Unrated ---
st.subheader("Rated vs Unrated Games")
fig4 = px.histogram(filtered, x="rated", color="rated", title="Rated vs. Unrated Games",
                    category_orders={"rated": [False, True]},
                    color_discrete_sequence=px.colors.qualitative.Safe)
st.plotly_chart(fig4, use_container_width=True)

# --- Plot 5: Most Common Time Increments ---
st.subheader("Most Common Time Increments")
setup = filtered[["time_increment"]].value_counts().reset_index()
setup.columns = ["Time Increment", "Count"]
setup = setup.head(10)
fig5 = px.bar(setup, x="Time Increment", y="Count", title="Top 10 Most Common Time Increments",
              color="Count", color_continuous_scale="Blues")
st.plotly_chart(fig5, use_container_width=True)

# --- Plot 6: Turns Distribution ---
st.subheader("Distribution of Turns per Game")
fig6 = px.histogram(filtered, x="turns", nbins=30, title="Distribution of Turns",
                    color_discrete_sequence=['skyblue'])
fig6.add_vline(x=avg_turns, line_dash="dash", line_color="red")
st.plotly_chart(fig6, use_container_width=True)

# --- Plot 7: Top Openings by Winrate (White wins) ---
st.subheader("Top 10 Openings with Best White Winrate")
openings = filtered[filtered["winner"] == "White"]["opening_shortname"].value_counts().head(10).reset_index()
openings.columns = ["Opening", "Wins"]
fig7 = px.bar(openings, x="Opening", y="Wins", title="Top 10 Openings with Best White Winrate",
              color="Wins", color_continuous_scale="OrRd")
st.plotly_chart(fig7, use_container_width=True)

# --- Plot 8: Top Players by Win Rate ---
st.subheader("Top 10 Players by Win Rate")
white_wins = filtered[filtered["winner"] == "White"]["white_id"].value_counts()
black_wins = filtered[filtered["winner"] == "Black"]["black_id"].value_counts()
total_wins = white_wins.add(black_wins, fill_value=0)
total_games = filtered["white_id"].value_counts().add(filtered["black_id"].value_counts(), fill_value=0)
winrate = (total_wins / total_games) * 100
player_stats = pd.DataFrame({"Games": total_games, "WinRate": winrate}).dropna().sort_values("Games", ascending=False).head(10)
player_stats = player_stats.reset_index().rename(columns={"index": "Player"})
fig8 = px.bar(player_stats, x="Player", y="WinRate", title="Top 10 Players by Win Rate (min games played)",
              color="WinRate", color_continuous_scale="Sunset")
st.plotly_chart(fig8, use_container_width=True)
