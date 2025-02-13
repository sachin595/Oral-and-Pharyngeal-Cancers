import streamlit as st
import pandas as pd
import numpy as np

import os
import gdown
from joblib import load
from sklearn.preprocessing import StandardScaler

model = load('OPC_model.joblib')
scalerX = load('OPC_scalerX.joblib')
scalerY = load('OPC_scalerY.joblib')

def predict(inputs):
    
    # Define the feature names expected by the model
    feature_names = ['Sex', 'Year', 'AgeGroup', 'Ethnicity', 'Race']
    
    # Mapping dictionaries
    sex_map = {'Male': 0, 'Female': 1}
    ethnicity_map = {'Hispanic': 1, 'Non-Hispanic': 0}
    race_map = {'White': 1, 'Black or African American': 0, 'Asian or Pacific Islander': 2, 'American Indian or Alaska Native': 3}
    agegroup_map = {
                    '1-4 years': 0,
                    '5-9 years': 1,
                    '10-14 years': 2,
                    '15-19 years': 3,
                    '20-24 years': 4,
                    '25-29 years': 5,
                    '30-34 years': 6,
                    '35-39 years': 7,
                    '40-44 years': 8,
                    '45-49 years': 9,
                    '50-54 years': 10,
                    '55-59 years': 11,
                    '60-64 years': 12,
                    '65-69 years': 13,
                    '70-74 years': 14,
                    '75-79 years': 15,
                    '80-84 years': 16,
                    '85+ years': 17
                    }
    
    
    # Apply mappings
    inputs['Sex'] = sex_map[inputs['Sex']]
    inputs['Ethnicity'] = ethnicity_map[inputs['Ethnicity']]
    inputs['Race'] = race_map[inputs['Race']]
    inputs['AgeGroup'] = agegroup_map[inputs['AgeGroup']]
    
    # Assuming the model expects a DataFrame with the same structure as during training
    input_df = pd.DataFrame([inputs], columns=feature_names)

    # Standardize the input data
    input_df_scaled = scalerX.transform(input_df)
    
    # Print input data for debugging
    #st.write('Input Data (Standardized):', input_df_scaled)
    
    prediction_scaled = model.predict(input_df_scaled)
    
    prediction = scalerY.inverse_transform(prediction_scaled)
    
    return prediction



# Streamlit user interface
st.title('Predictive Analytics for Oral and Pharyngeal Cancers')

# Creating form for input
with st.form(key='prediction_form'):
    sex = st.selectbox('Sex', options=['Male', 'Female'])
    year = st.selectbox('Year of Mortality Rate', options=list(range(1999, 2021)))
    agegroup = st.selectbox('Age Group', options=[
        '1-4 years', '5-9 years', '10-14 years', '15-19 years', '20-24 years', '25-29 years', '30-34 years', '35-39 years', '40-44 years',           '45-49 years', '50-54 years', '55-59 years', '60-64 years', '65-69 years', '70-74 years', '75-79 years', '80-84 years', '85+ years'
    ])
    ethnicity = st.selectbox('Ethnicity', options=['Hispanic', 'Non-Hispanic'])
    race =  st.selectbox('Race', options=['White','Black or African American', 'Asian or Pacific Islander', 'American Indian or Alaska Native'])
    
    submit_button = st.form_submit_button(label='Predict')

# Processing prediction
if submit_button:
    input_data = {
        'Sex': sex,
        'Year':year,
        'AgeGroup': agegroup, 
        'Ethnicity': ethnicity,
        'Race': race,
               
    }
    # Predict and decode
    y_pred = predict(input_data)  # Ensure predict() returns the appropriate numeric predictions
    #decoded_predictions = decode_predictions(y_pred.flatten())
    # Create a new array for the rounded predictions
    y_predicted_rounded = np.zeros_like(y_pred)

    # Round each column of y_pred separately to different decimal places
    y_predicted_rounded[:, 0] = np.round(y_pred[:, 0], 2)  # Round "Crude Rate" to 1 decimal place
    y_predicted_rounded[:, 1] = np.round(y_pred[:, 1], 4)  # Round "Survival Rate" to 9 decimal places
    # Get the rounded values
    crude_rate = y_predicted_rounded[0, 0]
    survival_rate = y_predicted_rounded[0, 1]

    # Format the survival rate with percentage
    formatted_survival_rate = f'{survival_rate * 100:.2f}%'

    # Display results in Streamlit
    st.markdown(f'**Crude Mortality Rate:** Number of deaths per 100,000 individuals in a given year\n\n**{crude_rate}**')
    st.markdown(f'**Survival Rate:** Likelihood of the Survival\n\n**{formatted_survival_rate}**')
  
