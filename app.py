
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

tuik_cpi = {
    "2022-01": 22.58, "2023-01": 72.45, "2024-01": 54.72, "2025-01": 56.35,
    "2022-05": 39.33, "2023-05": 63.72, "2024-05": 62.51
}

@app.route('/calculate-rent', methods=['POST'])
def calculate_rent():
    data = request.get_json()
    try:
        start_date_str = data['start_date']
        initial_rent = float(data['initial_rent'])
        property_type = data['property_type']
        today = datetime.today()

        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
        current_rent = initial_rent
        output_lines = []
        year = 1

        while start_date < today:
            end_date = start_date.replace(year=start_date.year + 1) - timedelta(days=1)
            label = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"

            if year == 1:
                output_lines.append(f"{label}: {current_rent:.2f} TL")
            else:
                increase_month = start_date.month
                increase_year = start_date.year
                index_month = (increase_month - 1) or 12
                index_year = increase_year if increase_month > 1 else increase_year - 1
                key = f"{index_year}-{str(index_month).zfill(2)}"
                cpi = tuik_cpi.get(key)
                if not cpi:
                    break  # CPI verisi yoksa hesaplamayı durdur

                if property_type.lower() == "konut" and datetime(2022, 6, 11) <= start_date <= datetime(2024, 7, 1):
                    cpi = 25.0
                current_rent *= (1 + cpi / 100)
                output_lines.append(f"{label}: {current_rent:.2f} TL (%{cpi})")

            start_date = start_date.replace(year=start_date.year + 1)
            year += 1

        return jsonify({"output": "\n".join(output_lines)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
