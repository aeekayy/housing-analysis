from flask import Flask, jsonify, request
import boto3
from botocore.exceptions import ClientError
import os
import datetime
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text
import psycopg2
import pandas

# initialize our Flask application
# SQLALCHEMY_DATABASE_URI = 'postgresql://farye:@localhost/test'

SQLALCHEMY_ECHO = True

app= Flask(__name__)

SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"].rstrip()
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["SQLALCHEMY_DATABASE_URI"].rstrip()
db = SQLAlchemy(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

class RentalProperty(db.Model):
    __tablename__ = "rental_property"
    rental_property_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=sa_text("uuid_generate_v4()"))
    address_1 = db.Column(db.String(256))
    city = db.Column(db.String(128))
    state = db.Column(db.String(8))
    zip = db.Column(db.String(16))
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    purchase_price = db.Column(db.Float())
    after_repair_price = db.Column(db.Float())
    purchase_closing_cost = db.Column(db.Float())
    repair_cost = db.Column(db.Float())
    down_payment_percentage = db.Column(db.Float())
    loan_interest_rate = db.Column(db.Float())
    rent_per_unit = db.Column(db.Float())
    rent_num_units = db.Column(db.Integer())
    property_taxes = db.Column(db.Float())
    insurance = db.Column(db.Float())

class RedfinHouse(db.Model):
    __tablename__ = "redfin_house"

    redfin_house_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=sa_text("uuid_generate_v4()"))
    address_1 = db.Column(db.String(256))
    city = db.Column(db.String(128))
    state = db.Column(db.String(8))
    zip = db.Column(db.String(16))
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    price = db.Column(db.Float())
    sale_type = db.Column(db.String(128))
    sold_date = db.Column(db.DateTime())
    property_type = db.Column(db.String(128))
    year_built = db.Column(db.Integer())
    beds = db.Column(db.Integer())
    bath = db.Column(db.Float())
    location = db.Column(db.String(128))
    square_feet = db.Column(db.Float())
    lot_size = db.Column(db.Float())
    days_on_market = db.Column(db.Integer())
    price_square_foot = db.Column(db.Float())
    hoa_month = db.Column(db.Float())
    house_url = db.Column(db.String(256))
    source = db.Column(db.String(128))
    mls_no = db.Column(db.String(16))
    status = db.Column(db.String(32))
    next_open_house_start_time = db.Column(db.DateTime())
    next_open_house_end_time =  db.Column(db.DateTime())
    favorite = db.Column(db.Boolean())
    interested = db.Column(db.Boolean()) 
    created_at = db.Column(db.DateTime(),server_default=sa_text("now()"))
    updated_at = db.Column(db.DateTime(),server_default=sa_text("now()"))

"""
class RedfinHouseGrade for storing the grades of houses checked
"""
class RedfinHouseGrade(db.Model):
    __tablename__ = "redfin_house_grade"
    redfin_house_grade_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=sa_text("uuid_generate_v4()"))
    redfin_house_id = db.Column(UUID(as_uuid=True))
    grade = db.Column(db.Float())
    created_at = db.Column(db.DateTime(),server_default=sa_text("now()"))
    updated_at = db.Column(db.DateTime(),server_default=sa_text("now()"))

"""
class RedfinHouseIngestChecksum for checking the checksum of a file for ingest
      if the file has been ingested already, it should be added to avoid reingestion
"""
class RedfinHouseIngestChecksum(db.Model):
    __tablename__ = "redfin_house_ingest_checksum"
    checksum_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=sa_text("uuid_generate_v4()"))
    checksum = db.Column(db.String(64))
    filename = db.Column(db.String(256))
    created_at = db.Column(db.DateTime(),server_default=sa_text("now()"))
    updated_at = db.Column(db.DateTime(),server_default=sa_text("now()"))

"""
class RedfinHousePriceEstimate for comparing the price of a house to the projected price of a house
"""
class RedfinHousePriceEstimate(db.Model):
    __tablename__ = "redfin_house_price_estimate"
    price_estimate_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=sa_text("uuid_generate_v4()"))
    house_id = db.Column(UUID(as_uuid=True))
    price = db.Column(db.Float())
    predicted_price = db.Column(db.Float())
    created_at = db.Column(db.DateTime(),server_default=sa_text("now()"))
    updated_at = db.Column(db.DateTime(),server_default=sa_text("now()"))
    
@app.route("/name", methods=["POST"])
def setName():
    if request.method=='POST':
        posted_data = request.get_json()
        data = posted_data['data']
        return jsonify(str("Successfully stored  " + str(data)))

@app.route("/message", methods=["GET"])
def message():
    posted_data = request.get_json()
    name = posted_data['name']
    return jsonify(" Hope you are having a good time " +  name + "!!!")

@app.route("/v1/instances", methods=["GET"])
def instances():
    response = ec2.describe_instances(Filters=[{'Name':'tag:aiWARE_Component','Values':['aiware-anywhere']}])
    instancesToReturn = list()
    singleInstance = dict()
    for reservation in response["Reservations"]:
        print(len(reservation["Instances"]))
        if len(reservation["Instances"]) < 1:
            return jsonify([])
        for instance in reservation["Instances"]:
            singleInstance['instanceId'] = instance["InstanceId"]
            singleInstance['ipAddress'] = instance["PrivateIpAddress"] if "PrivateIpAddress" in instance else "0.0.0.0"
            singleInstance['instanceType'] = instance["InstanceType"]
            singleInstance['status'] = instance["State"]["Name"]
            # retrieve the tag
            for tags in instance["Tags"]:
                if tags["Key"] == 'Requestor':
                    singleInstance['requestor'] = tags["Value"]
            instancesToReturn.append(singleInstance)
    return jsonify(instancesToReturn)

@app.route("/v1/startnew", methods=["POST"])
def startNew():
    if request.method=='POST':
        posted_data = request.get_json()
        try:
            requestor = posted_data['requestor']
            data = { "data": requestor }
        except:
            err = { "Error": "The requestor could not be retrieved" }
            return jsonify(err)
        newInstance = ec2.run_instances(LaunchTemplate={'LaunchTemplateId':aiwareLaunchTemplateId},InstanceType=default_instance_type,TagSpecifications=[{'ResourceType':'instance','Tags':[{'Key':'Requestor','Value':requestor}]}],MinCount=1,MaxCount=1,NetworkInterfaces=[{'DeviceIndex':0,'SubnetId':default_subnet_id,'Groups':default_security_groups}])
        return jsonify(newInstance)

@app.route("/v1/stopinstance", methods=["POST"])
def stopInstance():
    if request.method=='POST':
       posted_data = request.get_json()
       instance_id = posted_data['instance_id']
       terminate = ec2.terminate_instances(InstanceIds=[instance_id])
       return jsonify(terminate)

"""
def import_csv function for ingesting every file within the directory csv
"""
def import_csv():
   for filename in os.listdir('csv'):
      df = pandas.read_csv(filename)
      postgreSQLTable = "redfin_house"
      postgreSQLConnection = db.get_engine()
      try:
         frame           = df.to_sql(postgreSQLTable, postgreSQLConnection, index=False, if_exists='append');
      except ValueError as vx:
         print(vx)
      except Exception as ex:  
         print(ex)
      else:
         print("PostgreSQL Table %s has been created successfully."%postgreSQLTable);

def analyze_house(price, year_built, type):
   # Calculate the price factor
   normalized_price = price / 800000
   price_rating = 0
   price_weight = .6
   if normalized_price < 1:
      price_rating = 1
   elif normalized_price < 1.2:
      price_rating = .8
   else:
      price_rating = .6
   
   # Calculate the year factor 
   if isinstance(year_built, int):
      normalized_year = year_built / 2000
   else:
      normalized_year = 0.99
   year_rating = 0
   year_weight = .2
   if normalized_year >= 1:
      year_rating = 1
   elif normalized_year >= 0.99: # 1980/2000
      year_rating = .8
   elif normalized_year >= 0.985: # 1970/2000
      year_rating = .6
   else: 
      year_rating = .4 

   type_rating = 0
   type_weight = .2
   if type == 'Single Family Residential':
      type_rating = 1
   elif type == 'Townhouse':
      type_rating = 0.8
   else:
      type_rating = 0.6

   return (price_rating * price_weight) + (year_rating * year_weight) + (type_rating * type_weight)

#  main thread of execution to start the server
if __name__=='__main__':
    print("Using SQL string {}".format(SQLALCHEMY_DATABASE_URI))
    with app.app_context():
        db.create_all()
    # To be expanded later with indexing and checking for duplicates
    # import_csv()
    houses = RedfinHouse.query.all()
    for house in houses:
        print('For house {} at {} in {}, the grade is {}'.format(house.redfin_house_id, house.address_1, house.city,analyze_house(house.price, house.year_built, house.property_type)))
    app.run(host="0.0.0.0",port=8080,debug=True)
