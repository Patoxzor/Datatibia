from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/check_character', methods=['POST'])
def check_character():
    data = request.get_json()
    server = data.get('server')
    character_name = data.get('character_name')
    
    if not server or not character_name:
        return jsonify({"error": "Please provide both server and character_name in the request body"}), 400

    url = f'https://www.tibia.com/community/?subtopic=worlds&world={server}'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Tibia website: {e}")
        return jsonify({"error": f"Failed to retrieve data from Tibia website: {e}"}), 500
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    online_section = soup.find_all('tr', {'class': ['Odd', 'Even']})
    
    if not online_section:
        print("Failed to find the online characters section")
        return jsonify({"error": "Failed to find the online characters section"}), 500
    
    character_found = False
    for row in online_section:
        cols = row.find_all('td')
        if len(cols) > 0:
            char_link = cols[0].find('a')
            if char_link and character_name.lower() in char_link.text.lower().replace('\xa0', ' '):
                character_found = True
                break
    
    if character_found:
        message = f"The character '{character_name}' is online on server '{server}'."
    else:
        message = f"The character '{character_name}' is offline on server '{server}'."
    
    return jsonify({
        "server": server,
        "character_name": character_name,
        "is_online": character_found,
        "message": message
    })

@app.route('/test_connectivity', methods=['GET'])
def test_connectivity():
    url = 'https://www.tibia.com'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return jsonify({"message": "Successfully connected to Tibia website"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to Tibia website: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
