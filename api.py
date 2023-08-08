from flask import Flask, request, jsonify, json
from oauth2client.service_account import ServiceAccountCredentials
import gspread


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'creds.json', scope)
file = gspread.authorize(creds)
sheet = file.open('data_annotation').sheet1

app = Flask(__name__)


@app.route('/get_transcript', methods=['GET'])
def get_transcript():
    filename = request.args.get('filename')
    if filename is None:
        return jsonify({"error": "File Name not provided"}), 400
    try:
        cell = sheet.find(filename)
        row = cell.row
        column = 4  # Assuming transcript is in the second column (index 1)
        transcript = sheet.cell(row, column).value
        return jsonify({"transcript": transcript})
    except gspread.exceptions.CellNotFound:
        return jsonify({"error": "Server Error"}), 500


@app.route('/update_transcript', methods=['PATCH'])
def update_transcript():
    data = request.data.decode('utf-8')
    data_dict = json.loads(data)

    if data_dict['filename'] is None or data_dict['corrected'] is None:
        return jsonify({"error": "Credentials not provided"}), 400
    try:
        cell = sheet.find(data_dict['filename'])
        row = cell.row
        corrected_column = 5
        sheet.update_cell(row, corrected_column, data_dict['corrected'])
        return jsonify({"message": "Corrected transcript updated successfully"})
    except gspread.exceptions.CellNotFound:
        return jsonify({"error": "Server Error"}), 500
    

if __name__ == '__main__':
    app.run(debug=False)