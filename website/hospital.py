from flask import *
import warnings
import pandas as pd
import pdfkit
import numpy as np
import imgkit
from opencage.geocoder import OpenCageGeocode
from flask import Flask,request,render_template,jsonify
import statsmodels.api as sm
import os
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import plotly.offline as py
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode
from geopy.geocoders import Nominatim
from folium.plugins import HeatMap
from geopy.exc import GeocoderTimedOut
import folium
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from gmplot import *
dict={}
dict2={}
warnings.filterwarnings('ignore')
app = Flask(__name__)
@app.route('/')
def index():
    try:
        os.remove('static/temp_donor.jpg')
    except:
        pass
    return render_template('index.html')
@app.route('/values1')
def re1():
    return render_template('generic.html')
@app.route('/values2')
def re2():
    return render_template('elements.html')
@app.route("/values5")
def re6():
    data=pd.read_csv('result/donate.csv')

    def get_latlon(place):
        key = '300b6f3f7b4348e682e7aae2b4895b4c'
        geocoder = OpenCageGeocode(key)
        query = str(place) + ', Kerala , India'
        results = geocoder.geocode(query)
        lat = results[0]['geometry']['lat']
        lng = results[0]['geometry']['lng']
        return (lat, lng)

    places = data['location'].tolist()
    l = []
    for i in places:
        latlon = get_latlon(i)
        l.append(latlon)
    loca1 = [(x[0], x[1]) for x in l]
    import geopy
    cord = []
    coords_1 = (10.1956, 76.3866)
    for i in loca1:
        cord.append(geopy.distance.vincenty(coords_1, i).km)
    list_id = data['ID'].tolist()
    place = data['location'].tolist()
    mail = data['email'].tolist()
    loc_data = pd.DataFrame({'ID': list_id, 'location': place, 'Distance': cord, 'mail': mail})
    if (len(loc_data) <= 3):
        loc_data1 = loc_data.sort_values(['Distance'])
    else:
        loc_data1 = loc_data.sort_values(['Distance'])[0:3]
    a = loc_data1.location.tolist()
    b = loc_data1.mail.tolist()
    lat_yes = []
    lon_yes = []
    gmap3 = gmplot.GoogleMapPlotter(10.1956, 76.3866, 10)

    l1 = []
    for i in a:
        latlon = get_latlon(i)
        l1.append(latlon)

    for i in l1:
        lat_yes.append(i[0])
        lon_yes.append(i[1])
        gmap3.scatter(lat_yes, lon_yes, '#00FF00', size=10, marker=True)

        gmap3.heatmap(lat_yes, lon_yes)

    gmap3.draw('result/blood_map12.html')
    import os
    from Dmail import Gmail

    password = 'blood@123'
    sender_email ='donationblood5@gmail.com'
    subject = "Alert! Blood Request"

    message = """
    blood required in Appolo hospital for emergency case...please donate
    """



    for i in b:
        with Gmail(sender_email, password) as gmail:
            gmail.send_message(message, i, subject)



    return render_template('index.html')
@app.route('/values3')
def re3():
    try:
        os.remove('static/temp_donor.jpg')
    except:
        pass
    return render_template('donor.html')
@app.route('/values4',methods=['GET',"POST"])
def pati():
    try:
        os.remove('static/temp_donor.jpg')
    except:
        pass
    if request.method=='POST':
        value = np.random.randint(20, 100)
        id= request.form['p_id']
        id1 = [id]
        pat_data = pd.read_csv("static/patient.csv")
        data=pd.read_csv("static/data.csv")
        det = pat_data[pat_data.ID == id]
        b=det.empty
        det1=det.Blood_Group
        print(det1)
        pat_blood = det.Blood_Group.tolist()[0]
        print(pat_blood)
        com={'O-':['O-'],'O+':['O-','O+'],'B-':['O-','B-'],'B+':['O-','O+','B+','B-'],'A-':['O-','A-'],'A+':['O-','A-','A+','O+'],'AB-':['AB-','A-','B-','O-'],'AB+':['AB-','A-','B-','O-','A+','B+','AB+','O+']}
        b = com.get(pat_blood)
        print(b)
        data1 = pd.read_csv('result/donor_head.csv')
        columns = ['ID', 'Blood_Group','location','email','Month_Since_Last_Donation','Body_Temperature','Hemoglobin_content','Weight','Name','Phone Number']
        try:
            for i in b:
                df1 = data[data.Blood_Group == i][columns]
                data1 = data1.append(df1, ignore_index=True)
                print(df1)
            data1.to_csv('result/dummy.csv', index=False)
        except:
            data1.to_csv('result/dummy.csv', index=False)
        data = pd.read_csv("result/dummy.csv")
        new_data = pd.read_csv("static/newdata.csv")
        new_data['int'] = 1
        independentVar = ['Month_Since_Last_Donation', 'Body_Temperature', 'Hemoglobin_Content', 'Weight', 'int']
        model1 = sm.Logit(new_data['Donate_Blood'], new_data[independentVar])
        answer = model1.fit()
        coeffs = answer.params
        def y(int, Month_Since_Last_Donation, Body_Temperature, Hemoglobin_Content, Weight):
            return coeffs[4] + coeffs[0] * Month_Since_Last_Donation + coeffs[1] * Body_Temperature + coeffs[
                2] * Hemoglobin_Content + coeffs[3] * Weight

        l = []
        for i in range(len(data)):
            y1 = y(int, data['Month_Since_Last_Donation'][i], data['Body_Temperature'][i],
                   data['Hemoglobin_content'][i], data['Weight'][i])
            l.append(y1)
        l2 = []
        l3 = []
        for j in range(len(l)):
            p = np.exp(l[j]) / (1 + np.exp(l[j]))
            l2.append(p)
            if l2[j] > 0.5:
                l3.append(1)
            else:
                l3.append(0)
        data['Donate_Blood'] = l3
        dummy = data[data.Donate_Blood == 1]
        dummy.to_csv('result/donate.csv', index=False)
        d1 = pd.read_csv("result/donate.csv")
        di=d1['ID'].tolist()
        dn=d1['Name'].tolist()
        db=d1['Blood_Group'].tolist()
        dl=d1['location'].tolist()
        dp=d1['Phone Number'].tolist()
        dc=d1['email'].tolist()
        dict = {'Koothattukulam': 43.71212134980524,
                'Kothamangalam': 38.91815018160549,
                'Thripunithura': 21.427797644212397,
                'Kalamassery': 16.68579967375038,
                'Perumbavoor': 13.394142937636351,
                'Aluva': 2.8038112614274784,
                'Kochi': 32.18504724236136,
                'Muvattupuzha': 35.62037304447239,
                'Piravom': 37.19861057148781,
                'Thrikkakara': 20.1935245502539,
                'Paravur': 15.267338220833173,
                'kadavanthra': 27.234707476586628,
                'Kakkand': 27.535034252799687}

        c = []
        for i in dl:
            val = dict.get(i)
            c.append(val)
        print(c)
        new=pd.DataFrame({'ID':di,'Name':dn,'Blood_Group':db,'location':dl,'Phone Number':dp,'email':dc,'distance(km)':c})
        new.to_csv('result/new.csv',index=False)

        d12=pd.read_csv('result/new.csv')
        d12=d12.sort_values(by=['distance(km)'])
        a=d12.empty
        d12.to_html('templates/donor_result.html')
        d12.to_json('static/output.json', orient='records')
        imgkit.from_url('templates/donor_result.html', 'static/temp_donor'+str(value)+'.jpg')
        filename = 'static/temp_donor'+str(value)+'.jpg'

        return render_template('hello.html',filename=filename,empty=a,patients=b)
@app.route('/values',methods=['GET',"POST"])
def donor():
    if request.method=='POST':
        id= int(request.form['id'])
        id1 = [id]
        hemo = float(request.form['hemo'])
        hemo1 = [hemo]
        month = int(request.form['month'])
        month1 = [month]
        temp = float(request.form['temp'])
        temp1 = [temp]
        loc = request.form['loc']
        loc1 = [loc]
        weight = float(request.form['weight'])
        weight1 = [weight]
        blood = request.form['Blood_Group']
        blood1 = [blood]
        mail1=request.form['mail']
        mail2=[mail1]
        phone=int(request.form['Phone Number'])
        phone2=[phone]
        name=request.form['Name']
        name1=[name]

        blood_data = pd.read_csv("static/newdata.csv")
        new_blood_data=pd.read_csv("static/data.csv")
        # print(id,type(id),hemo,type(hemo))
        # dic = {'id': id, 'location': loc, 'month_since_last_donation': month}
        dict1 = {'ID': id1,'Name' :name1,'Blood_Group':blood1,'location': loc1,'Month_Since_Last_Donation':month1,'Body_Temperature':temp1,'Hemoglobin_content':hemo1,'Weight':weight1,'email':mail2,'Phone Number':phone2}
        # print(dict1)
        df = pd.DataFrame(dict1)
        df=df.values.flatten()
        if df[0] in (new_blood_data['ID'].tolist()):
            ind = new_blood_data['ID'].tolist().index(df[0])
            new_blood_data.iloc[ind, 1] = df[1]
            new_blood_data.iloc[ind, 2] = df[2]
            new_blood_data.iloc[ind, 3] = df[3]
            new_blood_data.iloc[ind, 4] = df[4]
            new_blood_data.iloc[ind, 5] = df[5]
            new_blood_data.iloc[ind, 6] = df[6]
            new_blood_data.iloc[ind, 7] = df[7]
            new_blood_data.iloc[ind, 8] = df[8]
            new_blood_data.iloc[ind, 9] = df[9]
            new_blood_data.to_csv("static/data.csv", index=False)
        else:
            dict1 = {'ID': id1,'Name' :name1, 'Blood_Group': blood1, 'location': loc1, 'Month_Since_Last_Donation': month1,
                     'Body_Temperature': temp1, 'Hemoglobin_content': hemo1, 'Weight': weight1,'email':mail2,'Phone Number':phone2}
            df = pd.DataFrame(dict1)
            new = new_blood_data.append(df,ignore_index=True)
            new.to_csv("static/data.csv",index=False)
        # df.to_csv("static/data1.csv",index=False)
        return render_template('index.html')



@app.route('/values123',methods=['GET',"POST"])
def patient_data():
    data=pd.read_csv("static/docter_data.csv")
    visit=pd.read_csv('static/patient.csv')
    history = ['heart problem', 'diabetic related issue', 'general issue', 'skin related issue', 'gas related issues',
               'geriatric related issues', 'kidney related isssues', 'issues with nervous system',
               'mental health related issues', 'cancer related issues']
    if request.method == 'POST':
        name = request.form['name']
        id=request.form['id']
        doctor=request.form['doctor']
        list=data[data["doctor_name"]==doctor].values.flatten().tolist()
        list1 = visit[visit["ID"] ==id ].values.flatten().tolist()
        room_no=list[0]
        p_issue=list[4]
        speci= list[2]
        issue=history[p_issue-1]
        fee=list[3]

        if list1[3]%2==0:
            pay=fee/2
        else:
            pay=fee
        pay = round(pay,2)
        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [''],
            }
        ]
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('work.html')
        output_from_parsed_template = template.render(p_name=name, p_id=id, doc=doctor, speci=speci,
                                                      issue=issue, pay=pay, room=room_no)
        with open("pdf.html", "w") as fh:
            fh.write(output_from_parsed_template)

        pdfkit.from_file('pdf.html', 'invoice.pdf')
        return render_template('index.html')

@app.route('/values21',methods=['GET',"POST"])
def patient():
    if request.method=='POST':
        data = pd.read_csv("static/docter_data.csv")
        name= request.form['name']
        name1 = name
        dob = request.form['dob']
        dob1 = dob
        age = int(request.form['age'])
        age1 = age
        place = request.form['place']
        place1 = place
        issue = int(request.form['issues'])
        issue1 = issue
        blood =request.form['Blood_Group']
        blood1 = blood
        pat_id = name + '_' + dob + '_' + str(age) + '_' + place
        data_temp = data[data['class'] == issue1]
        depart = data_temp.iloc[np.random.randint(0, len(data_temp)), 2]
        df4 = pd.read_csv('static/patient.csv')
        from csv import writer
        def append_list_as_row(file_name, list_of_elem):
            with open(file_name, 'a+', newline='') as write_obj:
                csv_writer = writer(write_obj)
                csv_writer.writerow(list_of_elem)
        new_list = []
        if pat_id in (df4['ID'].tolist()) and depart in (df4['Department'].tolist()):
            temp_num = df4['ID'].tolist().index(pat_id)
            print(temp_num)
            new_list = list(df4.iloc[temp_num, :])
            new_list[3] = new_list[3] + 1
            print(new_list[3])
            df4.iloc[temp_num, 3] = new_list[3]
            df4.to_csv('static/patient.csv', index=False)

        elif pat_id in (df4['ID'].tolist()) or depart not in (df4['Department'].tolist()):
            data_temp = data[data['class'] == issue1]
            new_list = [pat_id, depart, blood1, 1]
            append_list_as_row('static/patient.csv', new_list)
        else:
            data_temp = data[data['class'] == issue1]
            new_list = [pat_id, depart, blood1, 1]
            append_list_as_row('static/patient.csv', new_list)
        doct = data[data['specialization'] == depart]
        docter = doct.iloc[:, 1].tolist()
        len1 = len(docter)
        return render_template('receipt.html',doctor=docter,len1=len1,id=pat_id,name=name1)




if __name__ == '__main__':
    app.run(debug=True)

# import pandas as pd
#
# data = pd.DataFrame(columns = ['ID', 'Blood_Group','location','email'])
# data.to_csv('result/donor_head.csv',index=False)
# data