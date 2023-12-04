import os
import streamlit as st
from streamlit_option_menu import option_menu
from carte import main as carte_main
from apply import main as apply_main
from timelapess import app as timelapess_app
from splitmap import main as splitmap_main
from test import app as test_app
from recherche import app as recherche_app
from requete1 import app as Requete1_app
from requete2 import app as Requete2_app
from requete3 import app as Requete3_app
from Cocslider import main as Cocslider_main
from testerr import app as graph_app
import base64


class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title='Pondering',
                options=['Carte', 'Slider', 'Timelapse', 'Split Map', 'Popups', 'Recherche', 'Requete1', 'Requete2', 'Requete3', 'Slider COG','Graphes intéractifs'],
                icons=['house-fill'],
                menu_icon='chat-text-fill',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": '#99d8c9'},
                    "icon": {"color": "black","font-size": "23px"},
                    "nav-link": {"color": "black", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

          

        # Execute the selected app
        for app_info in self.apps:
            if app_info["title"] == app:
                # Run the selected app
                app_info["function"]()
                

# Create an instance of MultiApp
multi_app = MultiApp()

# Add your apps to the MultiApp instance
multi_app.add_app("Carte", carte_main)
multi_app.add_app("Slider", apply_main)
multi_app.add_app("Timelapse", timelapess_app)
multi_app.add_app("Split Map", splitmap_main)
multi_app.add_app("Popups", test_app)
multi_app.add_app("Recherche", recherche_app)
multi_app.add_app("Requete1", Requete1_app)
multi_app.add_app("Requete2", Requete2_app)
multi_app.add_app("Requete3", Requete3_app)
multi_app.add_app("Slider COG", Cocslider_main)
multi_app.add_app("Graphes intéractifs", graph_app)

# Run the MultiApp
multi_app.run()
