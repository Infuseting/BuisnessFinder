from flask import Flask, request
import json
import os


app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <form method="post" action="/search">
            Longitude: <input type="text" name="longitude"><br>
            Latitude: <input type="text" name="latitude"><br>
            Nombre de kilomètres: <input type="text" name="kilometre"><br>
            Type requi (laissez vide pour tous les types): <input type="text" name="type"><br>
            <input type="submit" value="Rechercher">
        </form>
    '''
    
@app.route('/search', methods=['POST'])
def search():
    from index import get_places_nearby, file_numero

    longitude = float(request.form['longitude'])
    latitude = float(request.form['latitude'])
    kilometre = int(request.form['kilometre']) * 1000
    type_requi = request.form.get('type', '').strip().lower()
    results = get_places_nearby(latitude, longitude, kilometre, type_requi)
    os.makedirs("assets", exist_ok=True)
    last_file = file_numero()
    with open(f"assets/{last_file}", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    output = "<h2>Résultats :</h2><ul>"
    for place in sorted(results, key=lambda x: (x.get("website") is not None, x.get("website") or ""), reverse=True):
        name = place.get("name", "Nom inconnu")
        address = place.get("address", "Adresse inconnue")
        website = place.get("website")
        if website == None:
            website_display = "non"
        else:
            website_display = f'<a href="{website}">ici</a>' if website else "non"
        output += f"<li>{name} - {address} - {website_display}</li>"
    output += "</ul>"
    return output

if __name__ == '__main__':
    app.run(debug=True)