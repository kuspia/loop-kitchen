from flask import Flask, jsonify, request , send_file
import os
from controller.controller import generateReport , REPORT_OUTPUT_PATH
from models.report_data import ReportDB
app = Flask(__name__)

@app.route('/trigger_report', methods=['POST'])
def trigger_report():
    report_id = generateReport()
    return jsonify({"report_id": report_id})

@app.route('/get_report', methods=['POST'])
def get_report():
    report_id = request.json['report_id']
    status = ReportDB.getStatusOf(report_id)
    if status == 'running':
        return jsonify({'message': 'running'})
    elif status == 'not_found':
        return jsonify({'message': 'not found'})
    else:
        return send_file(os.path.join('..',REPORT_OUTPUT_PATH,f'report_{report_id}.csv') , as_attachment=True)


app.run()