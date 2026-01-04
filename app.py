from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = 'ec21f43bb5ba4bfe8ff933057f361114'
API_URL = 'https://api.dhlexpresscommerce.com/v1/orders'

def get_flat_rate_by_country(country_code, total_price):
    country_code = country_code.upper()

    # USA logic
    if country_code == "US":
        if total_price >= 500:
            return 0  # Free shipping
        return 35

    # Europe zone
    elif country_code in ["AL", "AD", "AT", "BY", "BE", "BA", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "GR", "HU", "IS", "IE", "DE", "FR", "IT", "XK", "LV", "LI", "LT",
                          "LU", "MT", "MD", "MC", "ME", "NL", "MK", "NO", "PL", "PT", "RO", "SM", "RS", "SK", "SI", "ES", "SE", "CH", "UA", "GB", "VA"]:
        if total_price >= 500:
            return 0  # Discounted for Europe
        return 31

    # Gulf countries
    elif country_code in ["AE", "SA", "KW", "QA", "BH", "OM"]:
        if total_price >= 500:
            return 0
        return 28

    # Rest of world
    else:
        if total_price >= 500:
            return 70
        return 45


@app.route('/receive_order', methods=['POST'])
def receive_order():
    data = request.get_json()

    try:
        shipping = data["shipping_address"]
        total_price = float(data.get("total_price", 0))
        flat_rate = get_flat_rate_by_country(shipping["country_code"], total_price)
        
        print(f"Received order #{data['order_number']} from {shipping['country_code']} — Total: ${total_price}, Rate: ${flat_rate}")

        payload = {
            "orderNumber": data["order_number"],
            "consigneeFirstName": shipping["first_name"],
            "consigneeLastName": shipping["last_name"],
            "consigneeAddress1": shipping["address1"],
            "consigneeCity": shipping["city"],
            "consigneePostcode": shipping["postcode"],
            "consigneeCountryCode": shipping["country_code"],
            "freightValue": flat_rate,
            "shippingMethod": "DHL Express",
            "products": [
                {
                    "sku": "SKU123",
                    "description": "Product Example",
                    "quantity": 1,
                    "weight": 0.5
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return jsonify({"message": "Order sent to DHL successfully"}), 200
        else:
            return jsonify({"error": response.text}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
