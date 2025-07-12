import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import fitz  # pymupdf
from io import BytesIO

def beam_moment_calc():
    """彎矩計算函數"""
    st.title("Bending Moment Capacity Checking (CoP 2013 Clause 6.1.2)")
    
    fcu = st.number_input("Concrete strength (MPa)", min_value=20.0, max_value=100.0, value=30.0, key="moment_fcu")
    fy = st.number_input("Rebar strength (MPa)", min_value=250.0, max_value=500.0, value=460.0, key="moment_fy")
    b = st.number_input("Beam Width (mm)", min_value=100.0, max_value=1000.0, value=300.0, key="moment_b")
    d = st.number_input("Effective depth (mm)", min_value=100.0, max_value=2000.0, value=500.0, key="moment_d")
    
    # Added: Main rebar quantity and diameter
    num_rebars = st.number_input("Number of Main Rebars", min_value=1, max_value=20, value=2, key="moment_num_rebars")
    rebar_dia = st.number_input("Main Rebar Diameter (mm)", min_value=6.0, max_value=50.0, value=20.0, key="moment_rebar_dia")
    
    # Calculate As based on num_rebars and rebar_dia
    As = num_rebars * np.pi * (rebar_dia / 2) ** 2
    st.write(f"Calculated Main Reinforcement Area As = {As:.2f} mm²")
    
    if st.button("Bending Moment Capacity Calculation"):
        if fcu <= 45:
            beta = 0.9
        elif fcu <= 80:
            beta = 0.9 - (fcu - 45) * 0.005
        else:
            beta = 0.72
        
        x = (As * fy) / (0.567 * fcu * b * beta)
        
        if x > 0.5 * d:
            st.write("Warning: Reinforcement ratio too high, check design.")
        else:
            z = d - 0.45 * x
            Mu = 0.87 * fy * As * z / 1e6
            st.write(f"Calculated Bending Moment Capacity Mu = {Mu:.2f} kNm")
            st.write("Reference Clause: CoP 2013 Clause 6.1.2.")
    
    # Added: Beam section view
    if st.button("Show Beam Section View"):
        fig, ax = plt.subplots(figsize=(2, 3))
        # Draw beam rectangle (width b, height h = d + cover + dia/2, assume cover=25mm)
        cover = 25.0  # Assumed concrete cover
        h = d + cover + rebar_dia / 2
        ax.add_patch(plt.Rectangle((0, 0), b, h, fill=None, edgecolor='black'))
        
        # Draw main rebars as circles (assumed in one layer at bottom)
        rebar_y = cover + rebar_dia / 2  # Position from bottom
        spacing = (b - 2 * cover - rebar_dia) / (num_rebars - 1) if num_rebars > 1 else 0
        for i in range(num_rebars):
            rebar_x = cover + rebar_dia / 2 + i * spacing
            ax.add_patch(plt.Circle((rebar_x, rebar_y), rebar_dia / 2, color='gray'))
        
        ax.set_xlim(0, b)
        ax.set_ylim(0, h)
        ax.set_aspect('equal')
        ax.set_xlabel('Width (mm)')
        ax.set_ylabel('Height (mm)')
        ax.set_title('Beam Cross-Section View')
        st.pyplot(fig)

def beam_shear_calc():
    """剪力計算函數"""
    st.title("Beam Shear Capacity Checking (CoP 2013 Clause 6.1.2.5)")
    
    fcu = st.number_input("Concrete strength (MPa)", min_value=20.0, max_value=100.0, value=30.0, key="shear_fcu")
    fy = st.number_input("Rebar strength (MPa)", min_value=250.0, max_value=500.0, value=460.0, key="shear_fy")
    b = st.number_input("Beam Width (mm)", min_value=100.0, max_value=1000.0, value=300.0, key="shear_b")
    d = st.number_input("Effective depth (mm)", min_value=100.0, max_value=2000.0, value=500.0, key="shear_d")
    As = st.number_input("Main reinforcement Area (mm²)", min_value=0.0, max_value=10000.0, value=1000.0, key="shear_As")
    Asv = st.number_input("Shear reinforcement Area per each (mm²/支)", min_value=0.0, max_value=1000.0, value=200.0, key="shear_Asv")
    sv = st.number_input("Shear reinforcement Spacing (mm)", min_value=50.0, max_value=500.0, value=200.0, key="shear_sv")
    V = st.number_input("Design shear (kN)", min_value=0.0, max_value=1000.0, value=100.0, key="shear_V")
    
    if st.button("Beam Shear Capacity Calculation"):
        rho = 100 * As / (b * d)
        Vc = 0.79 * np.power(rho, 1/3) * np.power((fcu / 25), 1/3) * np.power((400 / d), 1/4) * b * d / 1.25 / 1e3
        
        Vsv = 0.87 * fy * Asv / sv * d
        
        Vu = Vc + Vsv
        if V > Vu:
            st.write("Warning: Design shear V exceeds shear capacity Vu, check design.")
        else:
            st.write(f"Result：Shear Capacity Vu = {Vu:.2f} kN (Vc = {Vc:.2f} kN, Vsv = {Vsv:.2f} kN)")
        st.write("Reference Clause: CoP 2013 Clause 6.1.2.5. Caution!：Simplified，Not considering deep beam and diagonal links")
        
        fig, ax = plt.subplots()
        ax.bar(['Vc', 'Vsv', 'Vu'], [Vc, Vsv, Vu])
        ax.set_ylabel('kN')
        ax.set_title('Shear Capacity Components')
        st.pyplot(fig)

def pdf_search():
    """PDF 條文搜索函數（顯示圖像）"""
    st.title("CoP Clauses Searching (Show PDF Pages")
    
    pdf_path = "CoP_SUC2013e.pdf"  # 確保 PDF 喺同一目錄
    search_term = st.text_input("Insert clauses (e.g. Clause 6.1.2)", key="pdf_search_term")
    
    if search_term:
        doc = fitz.open(pdf_path)
        results = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if search_term.lower() in text.lower():
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                img_bytes = pix.tobytes("png")
                results.append((page_num + 1, BytesIO(img_bytes)))
        
        if results:
            for page_num, img in results:
                st.write(f"Found on page {page_num}：")
                st.image(img, use_column_width=True)
        else:
            st.write("No results found.")
        doc.close()
