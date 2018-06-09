"""
The flask application package.
"""

from flask import Flask, render_template, request, jsonify,session
import pypyodbc as pyodbc
import sys
import time
import datetime
import os
from flask import render_template
import json
import pandas as pd

from uploadfile import uploadToADL, uploadToGA
# Remote Connection
connection_string = "Driver={ODBC Driver 13 for SQL Server};Server=tcp:rctbraj.database.windows.net,1433;Database=Optimove;Uid=rctbraj@rctbraj;Pwd=Maramari#5301;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
# Local Connection
#(localdb)\ProjectsV13;Initial Catalog=TestDb;Integrated Security=True;Connect Timeout=30;Encrypt=False;TrustServerCertificate=True;ApplicationIntent=ReadWrite;MultiSubnetFailover=False

app = Flask(__name__)


# In order to use session in flask you need to set the secret key in your application settings. 
# Secret key is a random key used to encrypt your cookies and save send them to the browser.
app.secret_key = 'RxeTECU4y6AaEWgL57JwtCC9'

uploadFolder = '/static/uploads'
dir_path = os.path.dirname(os.path.realpath(__file__))

@app.route('/', methods=['GET', 'POST'])
def home():
	if request.method == 'POST':
		# print(request)
		data = request.form
		# print(data)
		resp_dict = {}
        # check if file is provided by the user
		if len(session['filename']) > 0:
			filename = session['filename']
		try:
			query_string = "INSERT INTO GoogleAnalyticsUpload ( CAMPAIGN_ID, CAMPAIGN_NAME, CAMPAIGN_DETAILS, CAMPAIGN_OFFER_DETAILS, CAMPAIGN_COST, CAMPAIGN_START_DATE, CAMPAIGN_END_DATE, CAMPAIGN_FILE_NAME) VALUES('{}','{}','{}','{}','{}', '{}','{}','{}')".format(
				data['campaign_uniqueId'], 
				data['campaign_name'], 
				data['campaign_details'], 
				data['campaign_offer_details'],
				data['campaign_cost'],
				data['campaign_start'],
				data['campaign_end'],
				filename)
			
			db = pyodbc.connect(connection_string)
			cursor = db.cursor()
			cursor.execute(query_string)
			db.commit()
			db.close()
			resp_dict = { 'success': 'true', 'statusCode': '200'}
		except Exception as e:
			resp_dict = { 'error': 'Wrong params. Specifics: ' + str(e), 'statusCode': '400' }
				
		# Logic to store the data in the Cloud
		try:
			if data['got_file'] == 'true' and len(session['filename']) > 0:
				resp_dict = saveCsvToCloud()
			else:
				resp_dict = { 'error': 'Failed to save Campaign File to Cloud - 00', 'statusCode': '400'}
		except Exception as ext:
			resp_dict = { 'error': "Some Error Here: " + str(ext), 'statusCode': '400' }
		return jsonify(resp_dict)
	elif request.method == 'GET':
		return render_template('index.html')

@app.route('/fileupload', methods=['POST'])
def file_upload():	
	filename = ''
	try:
		file = request.files.get('file')
		if file:			
			filename = '{}'.format(datetime.datetime.now())	  # Original filename is replaced with datetime tokens to avoid duplicates  		
			filename = filename.replace(":", ".")			  # Replace : with .   
			file.save(os.path.join(dir_path + uploadFolder, filename))
			session['filename'] = filename
			resp_dict = { 'success': 'true', 'statusCode': '200', 'data': filename}
	except Exception as e:
		resp_dict = { 'error': 'Failed to upload file', 'statusCode': '400'}
	return jsonify(resp_dict)

@app.route('/data', methods=['GET'])
def searchData():
	try:
		query_string = "SELECT * FROM GoogleAnalyticsUpload"
		db = pyodbc.connect(connection_string)
		cursor = db.cursor()
		cursor.execute(query_string)
		query_results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
		resp_dict = { 'success': 'true', 'statusCode': '200', 'data': query_results}
		db.commit()
		db.close()
		return jsonify(resp_dict)
	except Exception as e:
		resp_dict = { 'error': str(e), 'statusCode': '400' }
		return jsonify(resp_dict)

def saveCsvToCloud():			
	try:				
		file_location = os.path.join(dir_path + uploadFolder, session['filename'])
		if len(file_location) > 0:
			uploadToADL(file_location)
			uploadToGA(file_location)
			return { 'success': 'true', 'statusCode': '200', 'fileUploaded':session['filename']}
		else:
			return { 'error': 'File Error', 'statusCode': '400'}	

	except Exception as e:
		return { 'error': 'Failed to save data to Cloud - 01. Specifics: ' + str(e), 'statusCode': '400'}


