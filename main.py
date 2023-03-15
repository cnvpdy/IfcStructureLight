import streamlit as st
#from tools import ifchelper
import json
import ifcopenshell
from pathlib import Path                                                    
from re import L                                                            
from typing import Optional                                                 
import streamlit.components.v1 as components    
import ifcopenshell.util.element as util
import pandas as pd
import numpy as np
import ifcopenshell.util
import ifcopenshell.util.element
import json

ifcPath = open(r".\file.txt","rt",encoding='utf-8').read()
model = ifcopenshell.open(ifcPath)
ifcValue = open(ifcPath).read().encode('utf-8')



##############사용되는 함수###############
frontend_dir = (Path(__file__).parent / "frontend-viewer").absolute()       #

_component_func = components.declare_component(                             #
	"ifc_js_viewer", path=str(frontend_dir)                                 #
)  

def ifc_js_viewer(                                                          #    
    url: Optional[str] = None,                                              #
):                                                                          #
    component_value = _component_func(                                      #
        url=url,                                                            #
    )                                                                       #
    return component_value  
##############사용되는 함수################

#세션################
session = st.session_state
session["ifc_js_response"] = ""
#세션#################



session.ifc_js_response = ifc_js_viewer(ifcValue)


