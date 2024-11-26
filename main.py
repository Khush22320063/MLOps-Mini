import streamlit as st
import pandas as pd
import os
import time
from backend_analysis import (
    load_dataset,
    train_model,
    calculate_predicted_demand,
    distribute_energy,
    generate_prediction_map,
    generate_distribution_map
)

# Set up the Streamlit app
st.set_page_config(page_title="Energy Prediction and Distribution", layout="wide")

# Load the dataset and train the model once during app startup
df = load_dataset()
model = train_model(df)

# Global variable to store the last result file path
last_result_file = None

# Define utility functions
def save_to_excel(df, prefix):
    """Save DataFrame to an Excel file."""
    global last_result_file
    timestamp = int(time.time())
    file_path = os.path.join("static", f"{prefix}_{timestamp}.xlsx")
    df.to_excel(file_path, index=False)
    last_result_file = file_path
    return file_path

# Create static directory if not exists
os.makedirs("static", exist_ok=True)

# Main UI
st.title("Energy Prediction and Distribution System")

# Tabs for navigation
tabs = st.tabs(["Energy Prediction", "Energy Distribution", "Download Results"])

# Energy Prediction Tab
with tabs[0]:
    st.header("Predict Energy Demand")
    date = st.date_input("Select Date")
    energy = st.number_input("Enter Predicted Energy (MW)", min_value=0.0, value=0.0)

    if st.button("Predict"):
        if not date:
            st.error("Please select a valid date.")
        else:
            predicted_demand_df = calculate_predicted_demand(df, str(date), model)
            heatmap_path = generate_prediction_map(predicted_demand_df)

            # Save results
            save_to_excel(predicted_demand_df, "predicted_demand")

            st.success("Prediction completed!")
            st.image(heatmap_path, caption="Predicted Demand Heatmap")
            st.download_button(
                label="Download Prediction Results",
                data=open(last_result_file, "rb").read(),
                file_name=os.path.basename(last_result_file),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Energy Distribution Tab
with tabs[1]:
    st.header("Distribute Energy")
    date = st.date_input("Select Date for Distribution")
    energy = st.number_input("Enter Total Available Energy (MW)", min_value=0.0, value=0.0)

    if st.button("Distribute"):
        if not date:
            st.error("Please select a valid date.")
        else:
            predicted_demand_df = calculate_predicted_demand(df, str(date), model)
            allocation_result_df = distribute_energy(energy, predicted_demand_df)
            heatmap_path = generate_distribution_map(allocation_result_df)

            # Save results
            save_to_excel(allocation_result_df, "energy_distribution")

            st.success("Distribution completed!")
            st.image(heatmap_path, caption="Energy Distribution Heatmap")
            st.download_button(
                label="Download Distribution Results",
                data=open(last_result_file, "rb").read(),
                file_name=os.path.basename(last_result_file),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Download Results Tab
with tabs[2]:
    st.header("Download Last Results")
    if last_result_file and os.path.exists(last_result_file):
        st.download_button(
            label="Download Last Result File",
            data=open(last_result_file, "rb").read(),
            file_name=os.path.basename(last_result_file),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No results available for download.")
