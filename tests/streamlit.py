def test_streamlit_dashboard():
    # Simulate interaction
    st.session_state["intersection"] = "Dal Lake"
    st.session_state["congestion_level"] = 8

    # Verify that the dashboard reflects the simulation results
    st.write("Green Light Duration: 30s")
    st.write("Yellow Light Duration: 5s")
    st.write("Red Light Duration: 40s")

    assert "Green Light Duration" in st.session_state
    assert "Yellow Light Duration" in st.session_state
    assert "Red Light Duration" in st.session_state
