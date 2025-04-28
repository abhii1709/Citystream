def test_ml_model_prediction(model):
    test_input = {"vehicle_count": 150, "congestion_level": 8}
    predicted_durations = model.predict(test_input)
    assert 10 <= predicted_durations["green"] <= 60  # Green duration between 10 and 60
    assert 5 <= predicted_durations["yellow"] <= 20  # Yellow duration between 5 and 20
    assert 20 <= predicted_durations["red"] <= 60  # Red duration between 20 and 60
