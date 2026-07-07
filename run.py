from app import create_app, initialize_sample_data

app = create_app()

if __name__ == '__main__':

    initialize_sample_data()
    

    app.run(debug=True, host='0.0.0.0', port=5000)