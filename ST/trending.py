import streamlit as st
from joblib import load
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from lightfm import LightFM
from lightfm.data import Dataset
import streamlit as st
import streamlit.components.v1 as components


def app():
    
    if st.session_state.user_handle:
        st.title ("Recommendation Tool")
        st.write('you are logged in as  '+st.session_state.user_handle)
        # Load your pre-trained LightFM model
        with open('model.joblib', 'rb') as f:
            model = load(f)

        # Load interactions and contraception methods data (replace with your data loading code)
        user_data = pd.read_csv('user_data.csv')
        contraception_methods = pd.read_csv('contraception_methods.csv')  # Replace with your data file
        ratings_data = pd.read_csv('ratings_data.csv')

        # Define user features column names (replace with your actual column names)
        user_features_col = ['Number_of_Pregnancies', 'STI_History', 'Allergy_Latex', 'Allergy_Spermicide', 'Allergy_Copper', 'Allergy_Adhesive',
                            'Contraception_Preference_Barrier', 'Contraception_Preference_Emergency', 'Contraception_Preference_Hormonal',
                            'Contraception_Preference_Reversible', 'preferred_period_Long term', 'preferred_period_Short term',
                            'Health_Conditions_Blood clots', 'Health_Conditions_Breast Cancer', 'Health_Conditions_Diabetes',
                            'Health_Conditions_Endometriosis', 'Health_Conditions_Heart disease', 'Health_Conditions_Hypertension',
                            'Health_Conditions_Liver disease', 'Health_Conditions_Migraines', 'Health_Conditions_Obesity',
                            'Health_Conditions_Stroke', 'Health_Conditions_none', 'Health_Conditions_other', 'age_bin_<= 25',
                            'age_bin_26 - 30', 'age_bin_31 - 45', 'age_bin_>= 45']

        st.title("Enter user info and preferences")

        # Get user input
        Age = st.slider("Age", min_value=18, max_value=45, value=25)
        Number_of_Pregnancies = st.number_input("Number of Pregnancies", min_value=0, value=0)
        STI_History = st.checkbox("STI History")
        Allergies = st.multiselect("Allergies", ["Latex", "Spermicide", "Copper", "Adhesive"])
        Health_Conditions = st.multiselect("Health Conditions", ["Blood clots", "Breast Cancer", "Diabetes", "Endometriosis", "Heart disease", "Hypertension", "Liver disease", "Migraines", "Obesity", "Stroke", "none", "other"])
        Contraception_Preference = st.selectbox("Contraception Preference", ["Barrier", "Emergency", "Hormonal", "Reversible"])
        Preferred_Period = st.selectbox("Preferred Period", ["Long term", "Short term"])

        # Create a button to trigger recommendations
        button_clicked = st.button("Get Recommendations")

        # Check if the button is clicked
        if button_clicked:
        # Prepare user features for the new user
            new_user_data = {col: 0 for col in user_features_col}

            if 18 <= Age <= 25:
                new_user_data['age_bin_<= 25'] = 1
            elif 26 <= Age <= 30:
                new_user_data['age_bin_26 - 30'] = 1
            elif 31 <= Age <= 45:
                new_user_data['age_bin_31 - 45'] = 1
            else:
                new_user_data['age_bin_>= 45'] = 1

            new_user_data['Number_of_Pregnancies'] = Number_of_Pregnancies
            new_user_data['STI_History'] = int(STI_History)
            for allergy in Allergies:
                allergy_key = 'Allergy_' + allergy
                if allergy_key in new_user_data:
                    new_user_data[allergy_key] = 1

            # Health Conditions
            for condition in Health_Conditions:
                condition_key = 'Health_Conditions_' + condition
                if condition_key in new_user_data:
                    new_user_data[condition_key] = 1
            if 'Contraception_Preference_' + Contraception_Preference in new_user_data:
                new_user_data['Contraception_Preference_' + Contraception_Preference] = 1
            if 'preferred_period_' + Preferred_Period in new_user_data:
                new_user_data['preferred_period_' + Preferred_Period] = 1

            # Convert user features to DataFrame
            new_user = pd.DataFrame(new_user_data, index=[0])

            # Convert DataFrame to CSR matrix
            new_user = csr_matrix(new_user)

            

            # Build interactions directly in the Streamlit application
            dataset = Dataset()
            dataset.fit(users=user_data['User_ID'], items=contraception_methods['Method_ID'])
            (interactions, weights) = dataset.build_interactions((x, y) for x,y in zip(ratings_data['User_ID'], ratings_data['Method_ID'])
                                                     if not any(user_data.loc[user_data['User_ID'] == User_ID][condition].iloc[0] == 1
                                                                for condition in Health_Conditions
                                                                if condition in contraception_methods.columns and contraception_methods.loc[contraception_methods[condition] == 1].empty)
                                                     and not any(user_data.loc[user_data['User_ID'] == User_ID][allergy].iloc[0] == 1
                                                                   for allergy in Allergies
                                                                   if allergy in contraception_methods.columns and contraception_methods.loc[contraception_methods[allergy] == 1].empty)
                                                     and not (STI_History and 'STI_Contraindicated' in contraception_methods.columns and not contraception_methods.loc[contraception_methods['STI_Contraindicated'] == 1].empty)
                                                    )

            # Generate recommendations for the new user
            scores_new_user = model.predict(user_ids=0, item_ids=np.arange(interactions.shape[1]), user_features=new_user)
            top_items_new_user = contraception_methods.iloc[np.argsort(-scores_new_user)]

            # Filter out methods conflicting with health conditions, allergies, and STI history
            conflicting_methods = set()

            # Filter conflicting methods based on health conditions
            for condition in Health_Conditions:
                condition_key = 'Health_Conditions_' + condition
                if condition_key in contraception_methods.columns:
                    conflicting_methods.update(contraception_methods[contraception_methods[condition_key] == 1].index)

            # Filter conflicting methods based on allergies
            for allergy in Allergies:
                allergy_key = 'Allergy_' + allergy
                if allergy_key in contraception_methods.columns:
                    conflicting_methods.update(contraception_methods[contraception_methods[allergy_key] == 1].index)

            # Filter conflicting methods based on STI history
            if STI_History and 'STI_Contraindicated' in contraception_methods.columns:
                conflicting_methods.update(contraception_methods[contraception_methods['STI_Contraindicated'] == 1].index)
            if 'Contraception_Preference_Reversible' in new_user_data and 'Health_Conditions_Endometriosis' not in new_user_data:
                # Prioritize copper IUD and LNG IUD for reversible preference and no endometriosis
                conflicting_methods -= set(contraception_methods[contraception_methods['Method_Name'].isin(['Copper IUD', 'LNG IUD'])].index)
            # Filter out conflicting methods from top recommendations
            filtered_recommendations = top_items_new_user[~top_items_new_user.index.isin(conflicting_methods)]
            top_recommendations = filtered_recommendations[['Method_Name']].head(3)

            st.subheader("Top Recommendations for User:")
            st.write(top_recommendations)
            st.components.v1.html("""
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
            <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
            <!--Start of Conferbot Script-->
                <script type="text/javascript">
                (function (d, s, id) {
                    var js, el = d.getElementsByTagName(s)[0];
                    if (d.getElementById(id)) return;
                    js = d.createElement(s);
                    js.async = true;
                    js.src = 'https://s3.ap-south-1.amazonaws.com/conferbot.defaults/dist/v1/widget.min.js';
                    js.id = id;
                    js.charset = 'UTF-8';
                    el.parentNode.insertBefore(js, el);
                    js.onload = function () {
                    var w = window.ConferbotWidget("6602f301638de9baab76fdf2", "fullpage_chat");
                    };
                })(document, 'script', 'conferbot-js');
                </script>
                <!--End of Conferbot Script-->
        """,
        height=600,
        
        )
            
    else:
        st.warning("You need to log in for access") 

if __name__ == "__main__":
    app()
