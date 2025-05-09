
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

tuik_cpi = {
    "2017-01": 7.76, "2017-02": 7.88, "2017-03": 8.21, "2017-04": 8.66, "2017-05": 9.09, "2017-06": 9.36,
    "2017-07": 9.44, "2017-08": 9.66, "2017-09": 9.98, "2017-10": 10.37, "2017-11": 10.87, "2017-12": 11.14,
    "2018-01": 11.23, "2018-02": 11.23, "2018-03": 11.14, "2018-04": 11.06, "2018-05": 11.10, "2018-06": 11.49,
    "2018-07": 12.00, "2018-08": 12.61, "2018-09": 13.75, "2018-10": 14.90, "2018-11": 15.63, "2018-12": 16.33,
    "2019-01": 17.16, "2019-02": 17.93, "2019-03": 18.70, "2019-04": 19.39, "2019-05": 19.91, "2019-06": 19.88,
    "2019-07": 19.91, "2019-08": 19.62, "2019-09": 18.27, "2019-10": 16.81, "2019-11": 15.87, "2019-12": 15.18,
    "2020-01": 14.52, "2020-02": 13.94, "2020-03": 13.33, "2020-04": 12.66, "2020-05": 12.10, "2020-06": 11.88,
    "2020-07": 11.51, "2020-08": 11.27, "2020-09": 11.47, "2020-10": 11.74, "2020-11": 12.04, "2020-12": 12.28,
    "2021-01": 12.53, "2021-02": 12.81, "2021-03": 13.18, "2021-04": 13.70, "2021-05": 14.13, "2021-06": 14.55,
    "2021-07": 15.15, "2021-08": 15.78, "2021-09": 16.42, "2021-10": 17.09, "2021-11": 17.71, "2021-12": 19.60,
    "2022-01": 22.58, "2022-02": 25.98, "2022-03": 29.88, "2022-04": 34.46, "2022-05": 39.33, "2022-06": 44.54,
    "2022-07": 49.65, "2022-08": 54.69, "2022-09": 59.91, "2022-10": 65.26, "2022-11": 70.36, "2022-12": 72.31,
    "2023-01": 72.45, "2023-02": 71.83, "2023-03": 70.57, "2023-04": 69.80, "2023-05": 68.25, "2023-06": 66.88,
    "2023-07": 65.73, "2023-08": 65.00, "2023-09": 64.50, "2023-10": 63.47, "2023-11": 62.02, "2023-12": 60.45,
    "2024-01": 58.51, "2024-02": 56.90, "2024-03": 55.40, "2024-04": 53.83
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
        current_year_start = start_date

        while True:
            current_year_end = current_year_start.replace(year=current_year_start.year + 1) - timedelta(days=1)
            if current_year_end > today:
                break

            label = f"{current_year_start.strftime('%d/%m/%Y')} - {current_year_end.strftime('%d/%m/%Y')}"

            if year == 1:
                output_lines.append(f"{label}: {current_rent:.2f} TL")
            else:
                increase_month = current_year_start.month
                increase_year = current_year_start.year

                if increase_month == 1:
                    index_month = 12
                    index_year = increase_year - 1
                else:
                    index_month = increase_month - 1
                    index_year = increase_year

                key = f"{index_year}-{str(index_month).zfill(2)}"
                cpi = tuik_cpi.get(key)

                # DEBUG LOG
                print(f"DEBUG: key = {key}, cpi = {cpi}, date = {current_year_start.strftime('%d/%m/%Y')}")

                if not cpi:
                    break

                if (property_type.lower() == "konut" and
                    datetime(2022, 6, 11) <= current_year_start <= datetime(2024, 7, 1)):
                    cpi = min(cpi, 25.0)

                current_rent *= (1 + cpi / 100)
                output_lines.append(f"{label}: {current_rent:.2f} TL (%{cpi} artış)")

            current_year_start = current_year_start.replace(year=current_year_start.year + 1)
            year += 1

        return jsonify({"output": "\n".join(output_lines)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
