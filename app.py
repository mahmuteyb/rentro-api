
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

tuik_cpi = {
    "2022-01": 22.58, "2022-04": 34.46, "2022-05": 39.33, "2022-09": 83.45,
    "2023-04": 57.50, "2023-05": 63.72, "2023-09": 65.07,
    "2024-04": 59.64, "2024-05": 62.51, "2024-09": 64.91,
    "2025-04": 56.35
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

        while True:
            end_date = start_date.replace(year=start_date.year + 1) - timedelta(days=1)
            if end_date > today:
                break

            label = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"

            if year == 1:
                output_lines.append(f"{label}: {current_rent:.2f} TL")
            else:
                increase_month = start_date.month
                increase_year = start_date.year
                if increase_month == 1:
                    index_month = 12
                    index_year = increase_year - 1
                else:
                    index_month = increase_month - 1
                    index_year = increase_year
                key = f"{index_year}-{str(index_month).zfill(2)}"
                cpi = tuik_cpi.get(key)

                # DEBUG LOG
                print(f"DEBUG: key = {key}, cpi = {cpi}, date = {start_date.strftime('%d/%m/%Y')}")

                if not cpi:
                    break

                if (property_type.lower() == "konut" and
                    datetime(2022, 6, 11) <= start_date <= datetime(2024, 7, 1)):
                    cpi = min(cpi, 25.0)

                current_rent *= (1 + cpi / 100)
                output_lines.append(f"{label}: {current_rent:.2f} TL (%{cpi} artış)")

            start_date = start_date.replace(year=start_date.year + 1)
            year += 1

        return jsonify({"output": "\n".join(output_lines)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
