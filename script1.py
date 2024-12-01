import streamlit as st
import requests
import random
import os
import tempfile
from streamlit_extras.app_state import AppState

# -----Storing the user's data locally-----
# Initialize AppState for persistent storage
state = AppState()

# Initialize history in AppState
if "history" not in state:
    state["history"] = []

# Function to add to history
def add_to_history(query):
    state["history"].append(query)
    state.sync()  # Save changes to local storage

# -----Constants for API-----
API_BASE_URL = "https://api.pinterest.com/v5"
ACCESS_TOKEN = "your_access_token_here"  # Replace with your Pinterest API token

# -----Helper Functions-----
# Extract board ID from board link
def extract_board_id(board_url):
    # Example board URL: https://www.pinterest.com/username/boardname/
    try:
        board_id = board_url.rstrip('/').split('/')[-1]  # Get the last part of the URL
        return board_id
    except IndexError:
        return None

# Get pins from a board
def get_pins_from_board(board_id):
    url = f"{API_BASE_URL}/boards/{board_id}/pins"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])  # 'items' contains the list of pins
    else:
        st.error(f"Failed to fetch pins: {response.status_code} {response.text}")
        return []

# Download 5 random images temporarily
def download_images(pins, num_images=5):
    if len(pins) < num_images:
        num_images = len(pins)

    random_pins = random.sample(pins, num_images)
    temp_dir = tempfile.mkdtemp()

    for i, pin in enumerate(random_pins):
        image_url = pin["image"]["original"]["url"]
        response = requests.get(image_url)

        if response.status_code == 200:
            with open(os.path.join(temp_dir, f"image_{i}.jpg"), "wb") as f:
                f.write(response.content)

    return temp_dir

# Generate Playlist Function
def generate_playlist(vibe):
    """
    Placeholder function to generate a playlist based on vibes.
    Replace this with API logic (e.g., YouTube API, Spotify API).
    """
    example_songs = {
        "chill and aesthetic vibes": ["Song A", "Song B", "Song C"],
        "artistic and colorful vibes": ["Song D", "Song E", "Song F"],
    }
    return example_songs.get(vibe, ["Song G", "Song H", "Song I"])

# -----Begin Main App-----
# Set up page layout
st.set_page_config(page_title="pinVibe", layout="wide")

# Sidebar for history
st.sidebar.title("Previous Vibes")
if state.history:
    for i, item in enumerate(state.history):
        st.sidebar.write(f"Query {i+1}: {item['type']} - {item['input']}")
else:
    st.sidebar.write("No queries yet.")

st.sidebar.write("---")
st.sidebar.write("This app was created with ❤️ using free APIs and tools.")

# Main app
st.title("🎵 pinVibe")
st.subheader("Turn your Pinterest boards or images into a custom playlist")

# Step 1: User input
st.write("Choose one of the options below to get started:")

# Option 1: Pinterest Board Link
pinterest_url = st.text_input("Paste your Pinterest board link here:")

# Option 2: Upload Images
uploaded_images = st.file_uploader("Or upload up to 5 images:", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

# Check if more than 5 images are uploaded
if len(uploaded_images) > 5:
    st.warning("You can only upload up to 5 images. Please remove some.")

# Step 2: Process Input
if st.button("Generate Playlist"):
    # Validate input: Ensure either Pinterest URL or uploaded images, not both or neither
    if (not pinterest_url and not uploaded_images) or (pinterest_url and uploaded_images) or ("pinterest.com" not in pinterest_url or "/board/" not in pinterest_url):
        st.error("Something went wrong. Please check your input and try again.")
    else:
        if pinterest_url:
            input_type = "Pinterest Board"
            input_value = pinterest_url

            # Extract the board ID from the Pinterest URL
            board_id = extract_board_id(pinterest_url)
            if not board_id:
                st.error("Could not extract board ID. Please check the Pinterest board link.")
            else:
                # Fetch pins from the board
                pins = get_pins_from_board(board_id)
                if pins:
                    st.write(f"Found {len(pins)} pins. Fetching 5 random images...")

                    # Download images
                    temp_dir = download_images(pins)
                    st.write("Randomly selected images:")

                    # Display images
                    for img_file in os.listdir(temp_dir):
                        st.image(os.path.join(temp_dir, img_file))

                    # Simulate vibe detection and playlist creation
                    vibe_description = "chill and aesthetic vibes"  # Placeholder
                    playlist = generate_playlist(vibe_description)

                    # Save to history
                    add_to_history({"type": input_type, "input": input_value, "vibe": vibe_description, "playlist": playlist})

                    # Display results
                    st.success(f"Generated a playlist based on {input_type}:")
                    st.write(f"Vibes: {vibe_description}")
                    for i, song in enumerate(playlist, start=1):
                        st.write(f"{i}. {song}")

        elif uploaded_images:
            input_type = "Uploaded Images"
            input_value = uploaded_images

            # Display uploaded images
            st.success("Uploaded images received. Proceeding to analyze...")
            for uploaded_file in uploaded_images:
                st.image(uploaded_file, caption=f"Uploaded image: {uploaded_file.name}")

            # Simulate vibe detection and playlist creation
            vibe_description = "artistic and colorful vibes"  # Placeholder
            playlist = generate_playlist(vibe_description)

            # Save to history
            add_to_history({"type": input_type, "input": [img.name for img in uploaded_images], "vibe": vibe_description, "playlist": playlist})

            # Display results
            st.success(f"Generated a playlist based on {input_type}:")
            st.write(f"Vibes: {vibe_description}")
            for i, song in enumerate(playlist, start=1):
                st.write(f"{i}. {song}")

