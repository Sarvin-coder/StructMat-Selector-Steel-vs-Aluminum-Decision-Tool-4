import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Steel vs Aluminium Structural Material Selection Tool
# Upgraded Interactive Version (User inputs + formulas)
# ---------------------------------------------------------

st.set_page_config(page_title="Steel vs Aluminium Tool", page_icon="⚙️", layout="centered")
st.title("⚙️ Steel vs Aluminium Structural Material Selection Tool")
st.write("Now interactive: users enter data → the app calculates using formulas → recommends the better material.")

# -----------------------------
# Material property data
# -----------------------------
steel = {
    "name": "Steel",
    "tensile_strength": 400,      # MPa
    "yield_strength": 250,        # MPa
    "E": 200,                     # GPa
    "density": 7850,              # kg/m3
    "cost": 3.0,                  # RM/kg
    "corrosion_rating": 2         # /5
}

aluminum = {
    "name": "Aluminium",
    "tensile_strength": 310,      # MPa
    "yield_strength": 275,        # MPa
    "E": 69,                      # GPa
    "density": 2700,              # kg/m3
    "cost": 12.0,                 # RM/kg
    "corrosion_rating": 5         # /5
}

# ---------------------------------------------------------
# Helper calculation functions (beam formulas from slides)
# ---------------------------------------------------------
def beam_udl_calculations(L, w_kN_m, b, h, mat):
    # Convert
    w = w_kN_m * 1000.0  # N/m

    # Step 1: Mmax
    Mmax = (w * (L**2)) / 8.0  # N·m

    # Step 2: I
    I = (b * (h**3)) / 12.0  # m^4

    # Step 3: stress sigma = M*c/I
    c = h / 2.0
    sigma = (Mmax * c) / I  # Pa
    sigma_MPa = sigma / 1e6

    # Material properties
    E = mat["E"] * 1e9  # Pa
    sigma_y = mat["yield_strength"]  # MPa

    # Step 4: FOS
    fos = sigma_y / sigma_MPa if sigma_MPa > 0 else float("inf")

    # Step 5: Deflection
    delta = (5 * w * (L**4)) / (384 * E * I)  # m
    delta_mm = delta * 1000.0

    # Step 6: Deflection limit (L/360)
    delta_allow = (L / 360.0) * 1000.0  # mm

    # Step 7/8: Volume & Mass
    V = b * h * L
    mass = mat["density"] * V

    # Step 9: Cost
    total_cost = mass * mat["cost"]

    return {
        "Mmax(Nm)": Mmax,
        "I(m4)": I,
        "Stress(MPa)": sigma_MPa,
        "FOS": fos,
        "Deflection(mm)": delta_mm,
        "Allowable(mm)": delta_allow,
        "PASS?": delta_mm <= delta_allow,
        "Volume(m3)": V,
        "Mass(kg)": mass,
        "Cost(RM)": total_cost
    }

# ---------------------------------------------------------
# Application 1: Beam Design (UDL) → FULL FORMULAS
# ---------------------------------------------------------
def application_1_beam_udl():
    st.subheader("Application 1: Beam Design (Simply Supported Beam + UDL)")
    st.write("User enters beam and load data. The tool calculates results for steel and aluminium and recommends the better one.")

    L = st.number_input("Beam span, L (m)", value=6.0, min_value=0.1)
    w = st.number_input("UDL load, w (kN/m)", value=12.0, min_value=0.0)
    b = st.number_input("Beam width, b (m)", value=0.10, min_value=0.001)
    h = st.number_input("Beam height, h (m)", value=0.20, min_value=0.001)

    if st.button("Run Beam Calculations ✅"):
        steel_res = beam_udl_calculations(L, w, b, h, steel)
        alu_res = beam_udl_calculations(L, w, b, h, aluminum)

        df = pd.DataFrame({
            "Metric": list(steel_res.keys()),
            "Steel": list(steel_res.values()),
            "Aluminium": list(alu_res.values())
        })
        st.dataframe(df, hide_index=True)

        # Decide winner: MUST pass deflection + lower cost / better FOS
        st.markdown("### ✅ Decision / Recommendation")

        steel_pass = steel_res["PASS?"]
        alu_pass = alu_res["PASS?"]

        if steel_pass and not alu_pass:
            st.success("✅ Final Recommendation: **STEEL** (Aluminium fails deflection/serviceability).")
        elif alu_pass and not steel_pass:
            st.success("✅ Final Recommendation: **ALUMINIUM** (Steel fails deflection/serviceability).")
        else:
            # Both pass or both fail → choose by cost then deflection
            if steel_res["Cost(RM)"] < alu_res["Cost(RM)"]:
                st.success("✅ Final Recommendation: **STEEL** (more cost-effective).")
            else:
                st.success("✅ Final Recommendation: **ALUMINIUM** (lighter / may be preferred if weight is priority).")

# ---------------------------------------------------------
# Application 2: Weight-based (user inputs geometry)
# ---------------------------------------------------------
def application_2_weight():
    st.subheader("Application 2: Weight-Based Selection (User Input)")
    st.write("Enter the beam dimensions. The app calculates mass for steel and aluminium.")

    L = st.number_input("Length L (m)", value=6.0, min_value=0.1)
    b = st.number_input("Width b (m)", value=0.10, min_value=0.001)
    h = st.number_input("Height h (m)", value=0.20, min_value=0.001)

    if st.button("Run Weight Comparison ✅"):
        V = b * h * L
        ms = steel["density"] * V
        ma = aluminum["density"] * V

        st.write(f"Steel Mass = {ms:.2f} kg")
        st.write(f"Aluminium Mass = {ma:.2f} kg")

        if ma < ms:
            st.success("✅ Recommendation: **ALUMINIUM** (lighter → better for weight reduction).")
        else:
            st.success("✅ Recommendation: **STEEL** (unlikely, but heavier geometry case).")

# ---------------------------------------------------------
# Application 3: Cost-based (user inputs geometry)
# ---------------------------------------------------------
def application_3_cost():
    st.subheader("Application 3: Cost-Based Selection (User Input)")
    st.write("Enter beam dimensions. The app estimates total cost using mass × cost/kg.")

    L = st.number_input("Length L (m)", value=6.0, min_value=0.1)
    b = st.number_input("Width b (m)", value=0.10, min_value=0.001)
    h = st.number_input("Height h (m)", value=0.20, min_value=0.001)

    if st.button("Run Cost Comparison ✅"):
        V = b * h * L
        steel_cost = (steel["density"] * V) * steel["cost"]
        alu_cost = (aluminum["density"] * V) * aluminum["cost"]

        st.write(f"Steel Estimated Cost = RM {steel_cost:.2f}")
        st.write(f"Aluminium Estimated Cost = RM {alu_cost:.2f}")

        if steel_cost < alu_cost:
            st.success("✅ Recommendation: **STEEL** (cheaper).")
        else:
            st.success("✅ Recommendation: **ALUMINIUM** (cheaper).")

# ---------------------------------------------------------
# Application 4: Corrosion (environment input)
# ---------------------------------------------------------
def application_4_corrosion():
    st.subheader("Application 4: Corrosion Resistance Selection")
    env = st.selectbox("Select environment:", ["Indoor (dry)", "Outdoor (normal)", "Coastal / Corrosive"])

    if st.button("Run Corrosion Recommendation ✅"):
        if env == "Coastal / Corrosive":
            st.success("✅ Recommendation: **ALUMINIUM** (better corrosion resistance).")
        else:
            st.success("✅ Recommendation: **STEEL** (cost-effective; corrosion can be protected with coating).")

# ---------------------------------------------------------
# Application 5: Structural element + priority input
# ---------------------------------------------------------
def application_5_element():
    st.subheader("Application 5: Structural Element Recommendation (With Priority)")
    element = st.selectbox("Select structural element:", ["Beam", "Column", "Slab", "Truss", "Frame"])
    priority = st.selectbox("Select main priority:", ["High Strength/Stiffness", "Low Cost", "Low Weight", "High Corrosion Resistance"])

    if st.button("Run Element Recommendation ✅"):
        if priority == "Low Weight":
            st.success("✅ Recommendation: **ALUMINIUM** (lightweight priority).")
        elif priority == "High Corrosion Resistance":
            st.success("✅ Recommendation: **ALUMINIUM** (better corrosion resistance).")
        elif priority == "
