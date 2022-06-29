import json
from web3 import Web3, HTTPProvider
from flask import Flask, render_template, request, session
from DBConnection import Db
import datetime
import time
import pyautogui
app = Flask(__name__)
app.secret_key="bbcc"
staticpath = "c:\\mainproject\\Election\\static\\"


# truffle development blockchain address
blockchain_address = 'http://127.0.0.1:7545'
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = 'C:\\mainproject\\Election\\node_modules\\.bin\\build\\contracts\\CollegeElection.json'
deployed_contract_address = '0x6b678C90D38b07a5d29Edc1951B190D583b94D91'


@app.route('/', methods=['post', 'get'])
def login():

    if request.method == "POST":
        username = request.form['user']
        password = request.form['pswd']
        d = Db()
        qry = " select * from login where username ='" + username + "' and pswd = '" + password +"'"
        res = d.selectOne(qry)
        if res is not None and res['type']=="Admin":
            return render_template('Admin/index.html')
        elif res is not None and res['type']=="Staff":
            session['staff_id']=res['login_id']
            re = d.selectOne("select dptname from department where staffid='"+ str(session['staff_id']) +"'")
            session['dpt']=re
            return render_template('Staff/index.html',d=session['dpt'])
        else:
            return '''<script>alert('Enter valid username and password');window.location='/'</script>'''

    else:
        return render_template('loginTemplate.html')


@app.route('/add_student',methods=['post','get'])
def add_student():
    if request.method=='POST':
        regno = request.form['regno']
        name = request.form['sname']
        course = request.form['course']  # dropdownlist
        dept = request.form['dept']  # dropdownlist
        img = request.files['fileField']  # image

        email = request.form['email']

        import random
        pswd =  random.randint(0000,9999)

        dt = time.strftime("%Y%m%d-%h%M%S")
        img.save(staticpath + "student_images\\" + dt + ".jpg")
        path = "/static/student_images/" + dt + ".jpg"

        d = Db()
        qry = "INSERT INTO student_details (Reg_no,s_name,Dept_name,Course,Image) VALUES ('" + regno + "','" + name + "','" + dept + "','" + course + "','" + path + "')"
        res = d.insert(qry)

        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        message2 = contract.functions.addStudent(name,regno,dept, course, str(path)).transact()
        message3 = contract.functions.addlogin(email, str(regno), str(pswd)).transact()
        res1 = []
        for i in range(blocknumber + 1, 222, -1):

            print(i)
            a = web3.eth.get_transaction_by_block(i, 0)
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)

        return ''' <script> alert("Inserted...!!!!");window.location="/add_student" </script>   '''

    return render_template('Admin/S_details.html')

@app.route('/view_student')
def viewstudent():

        data = []
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        print(blocknumber)

        res1 = []
        for i in range(blocknumber, 222, -1):
            a = web3.eth.get_transaction_by_block(i, 0)
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)
            if str(decoded_input[0]) == '<Function addStudent(string,string,string,string,string)>':
                res={}
                res['name'] = decoded_input[1]['_Name']
                res['regno'] = decoded_input[1]['_Regno']
                res['dept'] = decoded_input[1]['_Dept']
                res['course'] = decoded_input[1]['_Course']
                res['image'] = decoded_input[1]['_Image']
                res1.append(res)
                print(res1)
        return render_template('Admin/ViewStudent.html', data=res1)

@app.route('/view_student',methods=['post'])
def view_studentDetails():
    flag=0
    dname = request.form['textfield']
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    blocknumber = web3.eth.get_block_number()
    print(blocknumber)

    res1 = []
    for i in range(blocknumber, 222, -1):
        a = web3.eth.get_transaction_by_block(i, 0)
        decoded_input = contract.decode_function_input(a['input'])
        print(decoded_input)
        c=decoded_input[1]
        dp=dname.lower()

        if str(decoded_input[0]) == '<Function addStudent(string,string,string,string,string)>' and c['_Dept'].lower().find(dp)>=0:
            print( c['_Dept'].find(dname) )
            res = {}
            flag=1
            res['name'] = decoded_input[1]['_Name']
            res['regno'] = decoded_input[1]['_Regno']
            res['dept'] = decoded_input[1]['_Dept']
            res['course'] = decoded_input[1]['_Course']
            res['image'] = decoded_input[1]['_Image']
            res1.append(res)
            print(res1)
    if flag:
        return render_template('Admin/ViewStudent.html', data=res1)
    else:
        return ''' <script> alert("No student details available for this department...!!!!");window.location="/view_student" </script>   '''




@app.route('/vote')
def viewPage():
    s=session['regno']
    d1 = datetime.datetime.now()
    dt = d1.strftime("%d/%m/%Y %H:%M")
    if dt>="23/05/2022 08:00" and dt<="23/05/2022 23:59" :

        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        for i in range(blocknumber, 222, -1):
            a = web3.eth.get_transaction_by_block(i, 0)
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)
            c=decoded_input[1]
            if str(decoded_input[0]) == '<Function addVote(int256,string,string,string,string,string,string,string,string)>' and c['sid']==s:
                return ''' <script> alert("You already cast your vote...!!!!");window.location="/studloginpost" </script>   '''

        else:
            data = []
            with open(compiled_contract_path) as file:
                    contract_json = json.load(file)  # load contract info as JSON
                    contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
            contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
            blocknumber = web3.eth.get_block_number()

            res1 = []
            for i in range(blocknumber, 222, -1):
                    a = web3.eth.get_transaction_by_block(i, 0)
                    decoded_input = contract.decode_function_input(a['input'])
                    print(decoded_input)
                    res = {}
                    if str(decoded_input[0]) == '<Function addCandidate(string,string,string,string)>':

                        res['id'] = decoded_input[1]['_cid']
                        res['name'] = decoded_input[1]['_Name']
                        res['post'] = decoded_input[1]['_Post']
                        res['dept'] = decoded_input[1]['_Dept']
                        res1.append(res)

            return render_template('Student/S_vote.html',data=res1,s=session['studname'] )
    else:
        return ''' <script> alert("Voting will be start on May 23 at 8am...  ");window.location="/studloginpost" </script>   '''


@app.route('/vote',methods=['post','get'])
def vote():
    if request.method=='POST':
        try:
             chairperson = request.form['chairperson']
        except:
            return ''' <script> alert("Select a candidate for chairperson");window.location="/vote" </script>   '''
        try:
                vchairperson = request.form['v_chairperson']
        except:
                return ''' <script> alert("Select a candidate for vice chairperson");window.location="/vote" </script>   '''

        try:
                secretary = request.form['secretary']  # dropdownlist
        except:
                return ''' <script> alert("Select a candidate for secretary");window.location="/vote" </script>   '''

        try:
                editor = request.form['editor']  # dropdownlist
        except:
                return ''' <script> alert("Select a candidate for editor");window.location="/vote" </script>   '''
        try:
                artsec = request.form['artsSec']  # image
        except:
                return ''' <script> alert("Select a candidate for fine arts secretary ");window.location="/vote" </script>   '''

        try:
                grep = request.form['girlrep']
        except:
                return ''' <script> alert("Select a candidate for fine arts representitive of girls ");window.location="/vote" </script>   '''

        try:
                councilor = request.form['councilor']
        except:
                return ''' <script> alert("Select a candidate for councilor");window.location="/vote" </script>   '''


        sid=str(session['regno'])
        with open(compiled_contract_path) as file:
                contract_json = json.load(file)  # load contract info as JSON
                contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        message2 = contract.functions.addVote(blocknumber+1,str(sid),chairperson, vchairperson, secretary, editor, grep, councilor, artsec).transact()
        return ''' <script> alert("Vote Casted...!!!!");window.location="/Sindex" </script>   '''


@app.route('/approval')
def approve():
    d = Db()
    qry = "SELECT nomination.*,student_details.Reg_no,student_details.s_name FROM nomination INNER JOIN student_details ON nomination.Stud_reg_no=student_details.Reg_no and nomination.Attendance!=0 and nomination.Suspension_status!='Pending' "
    res= d.select(qry)
    if res:
        return render_template('Admin/Nom_appr.html', data=res)
    else:
          return ''' <script> alert("There is no nomination to approve  ");window.location="/Aindex" </script>   '''


@app.route('/approve_nomination/<n_id>')
def approve_nomination(n_id):
    da = datetime.datetime.now()
    dt = da.strftime("%d/%m/%Y %H:%M")
    if dt >= "09/05/2022 00:01" and dt <= "10/05/2022 23:59":
        d = Db()
        res = d.selectOne("SELECT * FROM nomination, student_details WHERE nomination.Stud_reg_no = student_details.Reg_no AND nomination.candidate_id = '" + n_id + "'")
        suspension = res['Suspension_status']
        arrears= res['Arrears']
        attend=res['Attendance']
        cname = res['s_name']
        post = res['Post_name']
        dept = res['Dept_name']

        if suspension == "no" and arrears==0 and attend>=75  :
            d = Db()
            d.update("update nomination set Approval_status = 'Approved' where Candidate_id ='"+ n_id +"'")

            with open(compiled_contract_path) as file:
                contract_json = json.load(file)  # load contract info as JSON
                contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
            contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
            blocknumber = web3.eth.get_block_number()

            print(blocknumber)

            message2 = contract.functions.addCandidate(str(n_id),cname,post,dept).transact()
            res1 = []
            for i in range(blocknumber+1,222,-1):

                print(i)

                a = web3.eth.get_transaction_by_block(i, 0)
                decoded_input = contract.decode_function_input(a['input'])
                print(decoded_input)

            return '''<script>alert('Nomination Approved');window.location='/approval'</script>'''

        else :
            d = Db()
            d.update("update nomination set Approval_status = 'Rejected' where Candidate_id ='" + n_id + "'")
            return '''<script>alert('Cannot approve this nomination');window.location='/approval'</script>'''

        return render_template('Admin/Nom_appr.html', data=res)

    else:
        return ''' <script> alert("Nomination can be approved between May 9th and 10th  ");window.location="/approval" </script>   '''

@app.route('/nomDetails')
def enter():
    d1 = datetime.datetime.now()
    dt = d1.strftime("%d/%m/%Y %H:%M")
    if  dt >= "06/05/2022 00:01" and dt <= "08/05/2022 23:00":
        login=session['staff_id']
        d = Db()
        qry1="select * from department where staffid="+str(login)
        res1=d.selectOne(qry1)
        dpt=res1['dptname']
        print(dpt)
        qry = "SELECT nomination.*,student_details.Reg_no,student_details.s_name FROM nomination INNER JOIN student_details ON nomination.Stud_reg_no=student_details.Reg_no and nomination.Approval_status='Pending' and nomination.Suspension_status='Pending' and nomination.Attendance=0 and student_details.Dept_name='"+dpt+"' "
        res3= d.select(qry)
        print(res3)
        if res3 ==[] :
            print("no details")
            return ''' <script> alert("Adding student details  is not pending for this department  ");window.location="/Stindex" </script>   '''

        else:
            return render_template('Staff/Dept_Candidate.html', data=res3, d=session['dpt'])
    else:
        return ''' <script> alert("Adding student Details is between May 6th and 8th ");window.location="/Stindex" </script>'''

@app.route('/nomDetails',methods=['post'])
def updateDetails():
    reg= request.form['rno']
    print(reg)
    suspension = request.form['radio']
    arrears = request.form['arrear']
    attendance = request.form['atten']
    d=Db()
    qry="update nomination set Suspension_status='"+ suspension +"',Arrears="+ arrears+",Attendance="+ attendance +" where Stud_reg_no='"+ reg+"'"
    res=d.update(qry)
    if res is not None:
        return render_template('Staff/index.html',d=session['dpt'])
    else:
        return ''' <script> alert("Details is not added  ");window.location="/Stindex" </script>   '''


@app.route('/Scandidate')
def getCandidate():
    d = datetime.datetime.now()
    dt = d.strftime("%d/%m/%Y %H:%M")
    if dt >= "11/05/2022 01:11":
        data = []
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        print(blocknumber)
        res1 = []
        for i in range(blocknumber, 222, -1):
            a = web3.eth.get_transaction_by_block(i, 0)
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input[0])
            if str(decoded_input[0]) == '<Function addCandidate(string,string,string,string)>':

                res = {}
                res['id'] = decoded_input[1]['_cid']
                res['name'] = decoded_input[1]['_Name']
                res['post'] = decoded_input[1]['_Post']
                res['dept'] = decoded_input[1]['_Dept']
                res1.append(res)

                print(res1)

        return render_template('Student/CandidateList.html',s=session['studname'],data=res1)
    else:
        return ''' <script> alert("Candidate List will be generated after completion of nomination and will published on May11  ");window.location="/studloginpost" </script>   '''


@app.route('/Acandidatelist')
def Candidate():
    d = datetime.datetime.now()
    dt = d.strftime("%d/%m/%Y %H:%M")
    if dt >= "11/05/2022 00:01":
        data = []
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        print(blocknumber)
        res1 = []
        for i in range(blocknumber,222, -1):
            a = web3.eth.get_transaction_by_block(i, 0)
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)
            if str(decoded_input[0]) == '<Function addCandidate(string,string,string,string)>':

                res = {}
                res['id'] = decoded_input[1]['_cid']
                res['name'] = decoded_input[1]['_Name']
                res['post'] = decoded_input[1]['_Post']
                res['dept'] = decoded_input[1]['_Dept']
                res1.append(res)

                print(res1)

        return render_template('Admin/CandidateList.html',data=res1)
    else:
        return ''' <script> alert("Candidate List will be generated after completion of nomination and will published on May11  ");window.location="/Aindex" </script>   '''


@app.route('/Stcandidatelist')
def Clist():

    d = datetime.datetime.now()
    dt = d.strftime("%d/%m/%Y %H:%M")
    if dt >= "11/05/2022 00:01":
        login = session['staff_id']
        d = Db()
        qry1 = "select * from department where staffid=" + str(login)
        res1 = d.selectOne(qry1)
        dpt = res1['dptname']
        data = []
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        print(blocknumber)
        res1 = []
        for i in range(blocknumber,222, -1):
            a = web3.eth.get_transaction_by_block(i, 0)
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)
            if str(decoded_input[0]) == '<Function addCandidate(string,string,string,string)>':

                res = {}
                res['id'] = decoded_input[1]['_cid']
                res['name'] = decoded_input[1]['_Name']
                res['post'] = decoded_input[1]['_Post']
                res['dept'] = decoded_input[1]['_Dept']
                res1.append(res)

                print(res1)

        return render_template('Staff/CandidateList.html',data=res1,d=session['dpt'])
    else:
        return ''' <script> alert("Candidate List will be generated after completion of nomination and will published on May11  ");window.location="/Stindex" </script>   '''


@app.route('/nomination', methods=['post','get'])
def addNomination():
    d = datetime.datetime.now()
    dt = d.strftime("%d/%m/%Y %H:%M")
    print(dt)
    if dt <"25/04/2022 07:00" and dt >"05/05/2022 23:00":
        return ''' <script> alert("Nomination can be given between April 25th and May 5th only ");window.location="/Sindex" </script>   '''

    if request.method=="POST":
        postname = request.form['postname'] # dropdownlist
        d = Db();
        res4 = d.selectOne("select * from nomination where Stud_reg_no= '" + str(session['regno']) + "'")
        if res4 is not None:
            return '''<script>alert('Already Addedd');window.location='/nomination'</script>'''
        else:
            qry2 = "INSERT INTO nomination VALUES ('','" + postname + "','Pending','" + str(session['regno']) + "',0,0,'Pending')"
            d.insert(qry2)
            return '''<script>alert('Addedd');window.location='/nomination'</script>'''

    else:

                d = Db();
                res3 = d.selectOne("select * from nomination where Stud_reg_no= '" + str( session['regno']) + "'")
                print(res3)
                return render_template('Student/S_nomination.html',s=session['studname'],data3=res3)


@app.route('/withdraw/<c_id>',methods=['post','get'])
def withdrawal(c_id):
        d = Db();
        qry = "DELETE FROM nomination where Candidate_id = '"+str(c_id)+"'  "
        d.delete(qry)
        return '''<script>alert('Your nomination has been withrawan ');window.location='/nomination'</script>'''

@app.route('/studlogin')
def studlogin():
    # python code for display alert messages

    pyautogui.alert("Press q to exit from camera frame")
    from camera import cam

    print("i")
    c = cam()
    u ,p ,r = c.camera()
    print(u)
    session['regno']= str(r)
    print(u)
    if u == "none":
        return '''<script>alert(' Invalid User');window.location='/'</script>'''
    else:
        d = Db()
        r = d.selectOne("select s_name from student_details where Reg_no='" + str(session['regno']) + "'")
        session['studname'] = r
        return render_template('Student/loginTemplate.html',data = u,data1=p)

@app.route('/studloginpost', methods=['post','get'])
def studloginpost():
    return render_template('Student/index.html',s=session['studname'])



@app.route('/Sresult')
def result():
    d = datetime.datetime.now()
    dt = d.strftime("%d/%m/%Y %H:%M")
    if dt>="24/05/2022 01:01":
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        res1 = []
        c_person = []
        v_cprsn = []
        sect = []
        ed = []
        ar = []
        grp = []
        counc = []
        flag=0
        for i in range(blocknumber, 222, -1):

            print(i)
            a = web3.eth.get_transaction_by_block(i, 0)
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)

            if str(decoded_input[0]) == '<Function addVote(int256,string,string,string,string,string,string,string,string)>':
                c = decoded_input[1]
                print(c)
                flag=1
                print("aaaa",c['chairperson'],i)
                c_person.append(c['chairperson'])
                v_cprsn.append(c['vchairperson'])
                sect.append(c['secretary'])
                ed.append(c['editor'])
                ar.append(c['artsec'])
                grp.append(c['grep'])
                counc.append(c['councilor'])

        print("cahir", c_person)
        print(len(c_person))
        if flag==1:
            d = {}
            for i in range(len(c_person) - 1):
                x = c_person[i]
                c = 0
                for j in range(i, len(c_person)):
                    if c_person[j] == c_person[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in d.keys():
                    d.update(count)
            print("chairperson", d)

            vice = {}
            for i in range(len(v_cprsn) - 1):
                x = v_cprsn[i]
                c = 0
                for j in range(i, len(v_cprsn)):
                    if v_cprsn[j] == v_cprsn[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in vice.keys():
                    vice.update(count)
            print("vicechairperson", vice)

            sectry = {}
            for i in range(len(sect) - 1):
                x = sect[i]
                c = 0
                for j in range(i, len(sect)):
                    if sect[j] == sect[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in sectry.keys():
                    sectry.update(count)
            print("secretary", sectry)

            editr = {}
            for i in range(len(ed) - 1):
                x = ed[i]
                c = 0
                for j in range(i, len(ed)):
                    if ed[j] == ed[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in editr.keys():
                    editr.update(count)
            print("editor", editr)

            artst = {}
            for i in range(len(ar) - 1):
                x = ar[i]
                c = 0
                for j in range(i, len(ar)):
                    if ar[j] == ar[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in artst.keys():
                    artst.update(count)
            print("art", artst)

            grprep = {}
            for i in range(len(grp) - 1):
                x = grp[i]
                c = 0
                for j in range(i, len(grp)):
                    if grp[j] == grp[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in grprep.keys():
                    grprep.update(count)
            print("grouprep", grprep)

            councl = {}
            for i in range(len(counc) - 1):
                x = counc[i]
                c = 0
                for j in range(i, len(counc)):
                    if counc[j] == counc[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in councl.keys():
                    councl.update(count)
            print("councellor", councl)

            chair_max_vote = max(zip(d.values(), d.keys()))[1]
            vice_max_vote = max(zip(vice.values(), vice.keys()))[1]
            sec_max_vote = max(zip(sectry.values(), sectry.keys()))[1]
            editor_max_vote = max(zip(editr.values(), editr.keys()))[1]
            artst_max_vote = max(zip(artst.values(), artst.keys()))[1]
            gr_max_vote = max(zip(grprep.values(), grprep.keys()))[1]
            c_max_vote = max(zip(councl.values(), councl.keys()))[1]

            db = Db()

            ch_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + chair_max_vote + "'")
            ch_vote = d[chair_max_vote]

            v_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + vice_max_vote + "'")
            v_vote = vice[vice_max_vote]

            se_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + sec_max_vote + "'")
            se_vote = sectry[sec_max_vote]

            ed_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + editor_max_vote + "'")
            ed_vote = editr[editor_max_vote]

            ar_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + artst_max_vote + "'")
            ar_vote = artst[artst_max_vote]

            gr_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + gr_max_vote + "'")
            gr_vote = grprep[gr_max_vote]

            co_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + c_max_vote + "'")
            co_vote = councl[c_max_vote]

            return render_template('Student/Result.html',s=session['studname'],data1=ch_details, c_vote=ch_vote, data2=v_details, v_vote1=v_vote, data3=se_details, vote3=se_vote, data4=ed_details, vote4=ed_vote, data5=ar_details, vote5=ar_vote, data6=gr_details, vote6=gr_vote, data7=co_details, vote7=co_vote )
    else:
        return '''<script>alert('Result will published after election ');window.location='/Sindex'</script>'''



@app.route('/Aresult')
def getresult():
    d = datetime.datetime.now()
    dt = d.strftime("%d/%m/%Y %H:%M")
    if dt >="24/05/2022 01:01":

        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        res1 = []
        c_person = []
        v_cprsn = []
        sect = []
        ed = []
        ar = []
        grp = []
        counc = []
        flag=0
        for i in range(blocknumber, 222, -1):

            print(i)
            a = web3.eth.get_transaction_by_block(i, 0)
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)
            c = []
            if str(decoded_input[0]) == '<Function addVote(int256,string,string,string,string,string,string,string,string)>':
                c = decoded_input[1]
                flag=1
                print("aaaa", c['chairperson'], i)
                c_person.append(c['chairperson'])
                v_cprsn.append(c['vchairperson'])
                sect.append(c['secretary'])
                ed.append(c['editor'])
                ar.append(c['artsec'])
                grp.append(c['grep'])
                counc.append(c['councilor'])

        print("cahir", c_person)
        print(len(c_person))
        if flag==1 :
            d = {}
            for i in range(len(c_person) - 1):
                x = c_person[i]
                c = 0
                for j in range(i, len(c_person)):
                    if c_person[j] == c_person[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in d.keys():
                    d.update(count)
            print("chairperson", d)

            vice = {}
            for i in range(len(v_cprsn) - 1):
                x = v_cprsn[i]
                c = 0
                for j in range(i, len(v_cprsn)):
                    if v_cprsn[j] == v_cprsn[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in vice.keys():
                    vice.update(count)
            print("vicechairperson", vice)

            sectry = {}
            for i in range(len(sect) - 1):
                x = sect[i]
                c = 0
                for j in range(i, len(sect)):
                    if sect[j] == sect[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in sectry.keys():
                    sectry.update(count)
            print("secretary", sectry)

            editr = {}
            for i in range(len(ed) - 1):
                x = ed[i]
                c = 0
                for j in range(i, len(ed)):
                    if ed[j] == ed[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in editr.keys():
                    editr.update(count)
            print("editor", editr)

            artst = {}
            for i in range(len(ar) - 1):
                x = ar[i]
                c = 0
                for j in range(i, len(ar)):
                    if ar[j] == ar[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in artst.keys():
                    artst.update(count)
            print("art", artst)

            grprep = {}
            for i in range(len(grp) - 1):
                x = grp[i]
                c = 0
                for j in range(i, len(grp)):
                    if grp[j] == grp[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in grprep.keys():
                    grprep.update(count)
            print("grouprep", grprep)

            councl = {}
            for i in range(len(counc) - 1):
                x = counc[i]
                c = 0
                for j in range(i, len(counc)):
                    if counc[j] == counc[i]:
                        c = c + 1
                count = dict({x: c})
                if x not in councl.keys():
                    councl.update(count)
            print("councellor", councl)

            chair_max_vote = max(zip(d.values(), d.keys()))[1]
            vice_max_vote = max(zip(vice.values(), vice.keys()))[1]
            sec_max_vote = max(zip(sectry.values(), sectry.keys()))[1]
            editor_max_vote = max(zip(editr.values(), editr.keys()))[1]
            artst_max_vote = max(zip(artst.values(), artst.keys()))[1]
            gr_max_vote = max(zip(grprep.values(), grprep.keys()))[1]
            c_max_vote = max(zip(councl.values(), councl.keys()))[1]

            db = Db()

            ch_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + chair_max_vote + "'")
            ch_vote = d[chair_max_vote]

            v_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + vice_max_vote + "'")
            v_vote = vice[vice_max_vote]

            se_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + sec_max_vote + "'")
            se_vote = sectry[sec_max_vote]

            ed_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + editor_max_vote + "'")
            ed_vote = editr[editor_max_vote]

            ar_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + artst_max_vote + "'")
            ar_vote = artst[artst_max_vote]

            gr_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + gr_max_vote + "'")
            gr_vote = grprep[gr_max_vote]

            co_details = db.selectOne(
                "SELECT * FROM `nomination`,`student_details` WHERE `nomination`.`Stud_reg_no`=`student_details`.`Reg_no` AND `nomination`.`Candidate_id`='" + c_max_vote + "'")
            co_vote = councl[c_max_vote]

            return render_template('Admin/Result.html',data1=ch_details, c_vote=ch_vote, data2=v_details, v_vote1=v_vote,
                                   data3=se_details, vote3=se_vote, data4=ed_details, vote4=ed_vote, data5=ar_details,
                                   vote5=ar_vote, data6=gr_details, vote6=gr_vote, data7=co_details, vote7=co_vote)
    else:
        return '''<script>alert('Election not completed yet...');window.location='/Aindex'</script>'''


@app.route('/Sindex')
def loadPage():
    return render_template('Student/index.html',s=session['studname'])

@app.route('/Aindex')
def lPage():
    return render_template('Admin/index.html')


@app.route('/Stindex')
def SPage():
    return render_template('Staff/index.html',d=session['dpt'])


if __name__ == '__main__':
    app.run()

