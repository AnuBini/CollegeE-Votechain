pragma solidity >=0.4.22 <0.9.0;

contract election {
    

    uint public studentCount = 0;
    mapping(uint => Student) public students;
    struct Student {
        uint Id;
        string Name;
        string Regno;
        string Dept;
        string Course;
        string Image;
    }
    uint public candidateCount = 0;
    mapping(uint => Candidate) public candidates;
    struct Candidate {
        uint blno;
        string cid;
        string Name;
        string Post;
        string Dept;
    }

    uint public Count = 0;
    mapping(uint => login) public loginDetails;
    struct login {
        uint Id;
        string name;
        string regno;
        string pswd;
    }
    function addlogin(string memory _name, string memory _regno, string memory _pswd) public {

        // Set parameters as required
        require(bytes(_name).length > 0);
        require(bytes(_regno).length > 0);
        require(bytes(_pswd).length > 0);

        // Check if requirements satisfied
        if (bytes(_name).length > 0 && bytes(_regno).length > 0 && bytes(_pswd).length > 0) {
            Count++;
            loginDetails[Count] = login(Count, _name, _regno, _pswd);
        }

    }

    function getlogin(uint _index) public view returns (string memory, string memory, string memory) {
        return (loginDetails[_index].name, loginDetails[_index].regno, loginDetails[_index].pswd);
    }



    function addStudent(string memory _Name, string memory _Regno, string memory _Dept, string memory _Course, string memory _Image) public {

        // Set parameters as required
        require(bytes(_Name).length > 0);
        require(bytes(_Regno).length > 0);
        require(bytes(_Dept).length > 0);
        require(bytes(_Course).length > 0);
        require(bytes(_Image).length > 0);

        // Check if requirements satisfied
        if (bytes(_Name).length > 0 && bytes(_Regno).length > 0 && bytes(_Dept).length > 0 && bytes(_Course).length > 0 && bytes(_Image).length > 0) {
            studentCount++;
            students[studentCount] = Student(studentCount, _Name, _Regno, _Dept, _Course, _Image);
        }

    }

    function getAllStudents(uint _index) public view returns (string memory, string memory, string memory, string memory, string memory) {
        return (students[_index].Name, students[_index].Regno, students[_index].Dept, students[_index].Course, students[_index].Image);
    }



    function addCandidate( string memory _cid,string memory _Name, string memory _Post, string memory _Dept) public {


        // Set parameters as required
        require(bytes(_Name).length > 0);
        require(bytes(_Post).length > 0);
        require(bytes(_Dept).length > 0);

       // Check if requirements satisfied

         if (bytes(_Name).length > 0 && bytes(_Post).length > 0 && bytes(_Dept).length > 0 ) {
            candidateCount++;

            candidates[candidateCount] = Candidate(candidateCount, _cid, _Name, _Post, _Dept );
        }
    }

     function viewCandidate(uint _index) public view returns (string memory, string memory, string memory, string memory ) {
        return (candidates[_index].cid, candidates[_index].Name, candidates[_index].Post, candidates[_index].Dept);
    }

   struct Vote{
       int voteid;
       string sid;
       string chairperson ;
       string vchairperson ;
       string secretary ;
       string editor ;
       string artsec ;
       string grep ;
       string councilor ;
   }
   Vote []emps;

   function addVote(
     int voteid, string memory sid,
     string memory chairperson ,
     string memory vchairperson ,
     string memory secretary ,
     string memory editor ,
     string memory artsec ,
     string memory grep ,
     string memory councilor
    ) public{
       Vote memory e
         =Vote (voteid,
                   sid,
                   chairperson ,
                   vchairperson ,
                   secretary ,
                    editor ,
                    artsec ,
                    grep ,
                    councilor
       );
       emps.push(e);
   }
    function getVote(
     int voteid
    ) public view returns(
     string memory,
     string memory,
     string memory,
     string memory,
     string memory,
     string memory,
     string memory,
     string memory
    ){
       uint i;
       for(i=0;i<emps.length;i++)
       {
           Vote memory e
             =emps[i];
           if(e.voteid==voteid)
           {
                  return(
                   e.sid,
                   e.chairperson ,
                   e.vchairperson ,
                    e.secretary ,
                    e.editor ,
                    e.artsec ,
                    e.grep ,
                    e.councilor
                  );
           }
       }
        return("0","0","0","0","0","0","0","0");
    }

}
