import streamlit as st
import pymongo



# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://ndutatracey:p431DOwzijLQGygw@cluster0.2mtghyy.mongodb.net/")
db = client["health_database"]


# Streamlit UI
def app():
    
    if st.session_state.user_handle:
        st.title(" Resources Finder")
        st.write('you are logged in as  '+st.session_state.user_handle)

        # Select resource type
        resource_type = st.selectbox("Select Resource Type", ["Clinics", "Online Pharmacies"])

        # Function to fetch resources based on type
        def fetch_resources(resource_type, query):
            collection = db[resource_type.lower().replace(" ", "_")]  # Get collection based on selected type
            return collection.find(query)

        # Search for resources
        st.subheader("Search Resources")
        query = st.text_input("Search by name")
        if st.button("Search"):
            resources = fetch_resources(resource_type, {"name": {"$regex": query, "$options": "i"}})
            for idx, resource in enumerate(resources):
                if idx > 0:
                    st.markdown("---")  # Add a divider between resources
                st.write(f"Name: {resource['name']}")
                st.write(f"Contact: {resource.get('contact', 'N/A')}")
                if resource_type == "Clinics":
                    st.write(f"Services Offered: {''.join(resource.get('services', []))}")
                elif resource_type == "Online Pharmacies":
                    st.write(f"Website: {resource.get('website', 'N/A')}")
        

    else:
        st.warning("You need to log in for access") 
                

if __name__ == "__main__":
    app()




    




