import streamlit as st
import ifcopenshell
from pathlib import Path                                                    
from typing import Optional                                                 
import streamlit.components.v1 as components    
import ifcopenshell.util
import ifcopenshell.util.element
import os
import clipboard

uploaded_file_ifc = st.sidebar.file_uploader("IFC Load",type=['ifc'],key="uploaded_file")
ifcValue = uploaded_file_ifc.getvalue()
# ifcPath = clipboard.paste()
# model = ifcopenshell.open(ifcPath)
# ifcValue = open(ifcPath).read().encode('utf-8')



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


os.system("pause")