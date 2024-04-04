import streamlit as st

from streamlit_option_menu import option_menu


import trending, test, your, about

DEFAULT_PAGE = "Account"
st.set_page_config(
        page_title="YourContraceptionChoice",
)



class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        # app = st.sidebar(
        with st.sidebar:        
            app = option_menu(
                menu_title='Choices for You ',
                options=['Home','Account', 'Recommendations', 'Directory'],
                icons=['house-fill', 'person-circle', 'trophy-fill', 'info-circle-fill'],
                menu_icon='chat-text-fill',
                default_index=1,
                styles={
                    "container": {"padding": "5!important","background-color":'violet'},
        "icon": {"color": "black", "font-size": "23px"}, 
        "nav-link": {"color":"black","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "white"},
        "nav-link-selected": {"background-color": "white"},}
                
                )

        
        
        if app == "Account":
            test.app() 
        if app == 'Home':
            about.app()           
        if app == "Recommendations":
            trending.app() 
        if app == 'Directory':
            your.app()
app = MultiApp()

# Add the apps
app.add_app("Account", test.app)
app.add_app("Home", about.app)
app.add_app("Recommendations", trending.app)
app.add_app("Directory", your.app)

# Run the default page
app.run()      
             
          
             
 
        
            
                
    
