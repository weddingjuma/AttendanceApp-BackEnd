from app import db
from app.Collections.Courses import Courses 
from app.Collections.Users import Users
from app.Collections.Departments import Departments
from pymongo.errors import WriteError
from flask import jsonify, make_response, Response
import datetime  
import jwt

from app.helpers.data_helper import get_student_rolls


class courseServices():
    
    @staticmethod
    def get_all_courses():
        courses = db['courses']
        return courses.find()
    
    
    @staticmethod
    def courseExists(courseName,department):
        courses = db['courses']
        return courses.find_one({"name":courseName,"department":department})
        
    @staticmethod
    def add_course(courseData):
        courses = db['courses']

        courseData.update({
            "student_enrolled":[]
        })
        
        responseData = {
            "status": 200,
            "result": {}
        }
        
        if(courseServices.courseExists(courseData['name'],courseData['department'])):
            responseData["result"] = {
                        "status":409,
                        "message": "course Already Exist"
                    }
        else:    
            try:
                courses.insert_one(courseData)
                responseData["result"]={
                            "status":201,
                            "message": "Course Create"
                        }
            except WriteError as werror:
                responseData["result"]={
                            "status":400,
                            "message": werror._message
                        }

        return make_response(responseData)
    
    
    @staticmethod
    def mark_present(student_roll,courseData):
        print("present : ",student_roll)
        print(courseData)
        
        courses = db['courses']
        
        print("=======================")
        print(datetime.datetime.utcnow().strftime("%Y-%m-%d"))
        print("=======================")
        
        doc = courses.find_one_and_update({**courseData,
                        # "attendance.date":datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                        # "attendance.attendance_on_date.roll_no":student_roll
                        },
                        {"$set": { "attendance.$[ele].attendance_on_date.$[rollno]":{"roll_no": student_roll,"status":True} }},
                        array_filters= [{"ele.date":datetime.datetime.utcnow().strftime("%Y-%m-%d")}
                                          ,{"rollno.roll_no": student_roll}],
                        upsert=True
                       )
        # print(doc)
        
    @staticmethod
    def mark_absent(student_roll,courseData):
        print("absent : ",student_roll)
        
        
    @staticmethod
    def mark_all_absent(courseData):
        courses = db['courses']
        
        if(not courses.find_one({**courseData
                             ,"attendance.date": datetime.datetime.utcnow().strftime("%Y-%m-%d")
        })):                        
            student_enrolled = courses.find_one({**courseData})['student_enrolled']
            student_rolls = get_student_rolls(student_enrolled)

            attendance_on_date = []
            for student_roll in student_rolls:
                student_attendance = {
                    "roll_no" : student_roll,
                    "status" : False
                }
                
                attendance_on_date.append(student_attendance)
            
            courses.update({**courseData},{"$push": {"attendance": {
                    "date": datetime.datetime.utcnow().strftime("%Y-%m-%d") ,
                    "attendance_on_date": attendance_on_date
                }}})
        