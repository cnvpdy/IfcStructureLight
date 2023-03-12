import streamlit as st
import ifcopenshell
#from tools import ifchelper
import json
import ifcopenshell
from pathlib import Path                                                    
from re import L                                                            
from typing import Optional                                                 
import streamlit.components.v1 as components    
import ifcopenshell.util.element as util


session = st.session_state 







def get_project_name():
    return session.ifc_file.by_type("IfcProject")[0].Name

def change_project_name():
    if session.project_name_input:
        session.ifc_file.by_type("IfcProject")[0].Name = session.project_name_input





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


def draw_3d_viewer():
    def get_current_ifc_file():
        return session.array_buffer
    session.ifc_js_response = ifc_js_viewer(get_current_ifc_file())



def format_ifcjs_psets(ifcJSON):
    """
    Organise pset data from web-ifc-api response
    """
    dict= {}
    for pset in ifcJSON:
        if "Qto" in pset["Name"]["value"]:
            for quantity in pset["Quantities"]:
                quantity_name = quantity["Name"]["value"]
                quantity_value = ""
                for key in quantity.keys():
                    if "Value" in key:
                        quantity_value = quantity[key]["value"]
                # quantity_value = quantity[5]["value"]
                if pset["expressID"] not in dict:
                    dict[pset["expressID"]] = {
                        "Name":pset["Name"]["value"], 
                        "Data":[]
                    }
                dict[pset["expressID"]]["Data"].append({
                    "Name": quantity_name,
                    "Value": quantity_value
                })
        if "Pset" in pset["Name"]["value"]:
            for property in pset["HasProperties"]:
                property_name = property["Name"]["value"]
                property_value = ""
                for key in property.keys():
                    if "Value" in key:
                        property_value = property[key]["value"]
                # property_value = property[5]["value"]
                if pset["expressID"] not in dict:
                    dict[pset["expressID"]] = {
                        "Name":pset["Name"]["value"], 
                        "Data":[]
                    }
                dict[pset["expressID"]]["Data"].append({
                    "Name": property_name,
                    "Value": property_value
                })
    return dict


def format_ifc_js_psets(data):
    return format_ifcjs_psets(data)

 

def get_object_data(fromId=None):
    def add_attribute(prop, key, value):
        if isinstance(value, tuple) and len(value) < 10:
            for i, item in enumerate(value):
                add_attribute(prop, key + f"[{i}]", item)
            return
        elif isinstance(value, tuple) and len(value) >= 10:
            key = key + "({})".format(len(value))
        
        propy = {
            "name": key,
            "string_value": str(value),
            "int_value": int(value.id()) if isinstance(value, ifcopenshell.entity_instance) else None,
        }
        prop.append(propy)
            
    if session.BIMDebugProperties:
        initialise_debug_props(force=True)
        step_id = 0
        if fromId:
            step_id =  int(fromId)
        else:
            step_id = int(session.object_id) if session.object_id else 0
        debug_props = st.session_state.BIMDebugProperties
        debug_props["active_step_id"] = step_id
        
        crumb = {"name": str(step_id)}
        debug_props["step_id_breadcrumb"].append(crumb)
        element = session.ifc_file.by_id(step_id)
        debug_props["inverse_attributes"] = []
        debug_props["inverse_references"] = []
        
        if element:
        
            for key, value in element.get_info().items():
                add_attribute(debug_props["attributes"], key, value)

            for key in dir(element):
                if (
                    not key[0].isalpha()
                    or key[0] != key[0].upper()
                    or key in element.get_info()
                    or not getattr(element, key)
                ):
                    continue
                add_attribute(debug_props["inverse_attributes"], key, getattr(element, key))
            
            for inverse in session.ifc_file.get_inverse(element):
                propy = {
                    "string_value": str(inverse),
                    "int_value": inverse.id(),
                }
                debug_props["inverse_references"].append(propy)
                
            print(debug_props["attributes"])

    
#디버그를 하기 위한 딕셔너리 BIMDebugProperties를 초기화하는 함수
def initialise_debug_props(force=False):
    if not "BIMDebugProperties" in session:
        session.BIMDebugProperties = {
            "step_id": 0,
            "number_of_polygons": 0,
            "percentile_of_polygons": 0,
            "active_step_id": 0,
            "step_id_breadcrumb": [],
            "attributes": [],
            "inverse_attributes": [],
            "inverse_references": [],
            "express_file": None,
        }
    if force:
        session.BIMDebugProperties = {
            "step_id": 0,
            "number_of_polygons": 0,
            "percentile_of_polygons": 0,
            "active_step_id": 0,
            "step_id_breadcrumb": [],
            "attributes": [],
            "inverse_attributes": [],
            "inverse_references": [],
            "express_file": None,
        }

def callback_upload():
    session["file_name"] = session["uploaded_file"].name
    session["array_buffer"] = session["uploaded_file"].getvalue()

    session["ifc_file"] = ifcopenshell.file.from_string(session["array_buffer"].decode("utf-8"))
    session["is_file_loaded"] = True
    
    ### Empty Previous Model Data from Session State
    session["isHealthDataLoaded"] = False
    session["HealthData"] = {}
    session["Graphs"] = {}
    session["SequenceData"] = {}
    session["CostScheduleData"] = {}

    ### Empty Previous DataFrame from Session State
    session["DataFrame"] = None
    session["Classes"] = []
    session["IsDataFrameLoaded"] = False

    
#streamlit의 세션을 만듦
session = st.session_state

#페이지의 기본적인 설정을 함
st.set_page_config(layout= "wide", page_title="가단면설계", page_icon="")

#사이드바에 파일업로드버튼을 만듦 (이때 변화가 생기면 callback_upload가 실행됨)
st.sidebar.file_uploader( label="IFC 로드", type=['ifc'], key="uploaded_file", on_change=callback_upload)
if "is_file_loaded" in session and session["is_file_loaded"]:
    st.sidebar.success(f'로드 완료')

    walls = session["ifc_file"].by_type('IfcWall')
    for wall in walls:
        st.write(wall.is_a())
        st.write(wall.Name)






#계속알아봐야함
initialise_debug_props()


#세션에 ifc_file 있을 경우와 ifc_file데이터에 true일 경우 코드 실행
if "ifc_file" in session and session["ifc_file"]:

    # 세션에 ifc_js_response값이 없을 경우 ifc_js_response에 ""를 입력해서 넣음
    if "ifc_js_response" not in session:
        session["ifc_js_response"] = ""
    
    #sidebar생성
    sidebar = st.sidebar
    #sidebar에 다음 코드 실행
    with sidebar:
        st.subheader("데이터")
        data = ""
        if session.ifc_js_response:
            data =  json.loads(session.ifc_js_response)
        

        if data:
            get_object_data(data['id'])
        else:
            st.write("")


        if "BIMDebugProperties" in session and session.BIMDebugProperties:
            props = session.BIMDebugProperties
            if props["attributes"]:
                st.subheader("Attributes")
                # st.table(props["attributes"])
                for prop in props["attributes"]:
                    col2, col3 = st.columns([3,3])
                    if prop["int_value"]:
                        col2.text(f'🔗 {prop["name"]}')
                        col2.info(prop["string_value"])
                        col3.write("🔗")
                        col3.button("Get Object", key=f'get_object_pop_button_{prop["int_value"]}', on_click=get_object_data, args=(prop["int_value"],))
                    else:
                        col2.text_input(label=prop["name"], key=prop["name"], value=prop["string_value"])
                        # col3.button("Edit Object", key=f'edit_object_{prop["name"]}', on_click=edit_object_data, args=(props["active_step_id"],prop["name"]))
                        
            if props["inverse_attributes"]:
                st.subheader("Inverse Attributes")
                for inverse in props["inverse_attributes"]:
                    col1, col2, col3 = st.columns([3,5,8])
                    col1.text(inverse["name"])
                    col2.text(inverse["string_value"])
                    if inverse["int_value"]:
                        col3.button("Get Object", key=f'get_object_pop_button_{inverse["int_value"]}', on_click=get_object_data, args=(inverse["int_value"],))
            
            ## draw inverse references
            if props["inverse_references"]:
                st.subheader("Inverse References")
                for inverse in props["inverse_references"]:
                    col1, col3 = st.columns([3,3])
                    col1.text(inverse["string_value"])
                    if inverse["int_value"]:
                        col3.button("Get Object", key=f'get_object_pop_button_inverse_{inverse["int_value"]}', on_click=get_object_data, args=(inverse["int_value"],))
    

            
    draw_3d_viewer()
    if data:
        st.subheader("데이터")
        psets = format_ifc_js_psets(data['props'])
        for pset in psets.values():
            st.subheader(pset["Name"])
            st.table(pset["Data"])  
 



else:
    st.header("◀ IFC파일을 로드하세요.")






# if __name__ == "__main__":
#     session = st.session_state
#     main()
#     execute()




