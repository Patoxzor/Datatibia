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
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve data from Tibia website"}), 500
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar a seção que contém a lista de personagens online
    online_section = soup.find_all('tr', {'class': ['Odd', 'Even']})
    
    if not online_section:
        return jsonify({"error": "Failed to find the online characters section"}), 500
    
    # Percorrer as linhas da tabela para verificar os personagens
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

if __name__ == '__main__':
    app.run(debug=True)
