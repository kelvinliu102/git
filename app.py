import streamlit as st
from functions import beam_moment_calc, beam_shear_calc, pdf_search  # 調用獨立函數

st.set_page_config(page_title="Reinforced Concrete Design Tools", layout="wide")

# 主目錄（側邊欄）
menu = st.sidebar.radio(
    "Main Menu",
    ["Beam Bending design", "Beam Shear design", "COP Concrete Clauses Search"]
)

# 根據選擇調用函數
if menu == "Beam Bending design":
    beam_moment_calc()
elif menu == "Beam Shear design":
    beam_shear_calc()
elif menu == "COP Concrete Clauses Search":
    pdf_search()
