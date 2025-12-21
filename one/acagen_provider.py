"""
AcaGen-style Student and Faculty Profile Generator.
Logic consistent with a academic-doc-generator (US Focused).
"""
import random
import string
from datetime import datetime, timedelta

class AcaGenProvider:
    # 精确的美国大学数据库 (100% 真实地址与官方 Logo)
    UNIVERSITIES = [
        {
            "name": "Arizona State University", 
            "short": "ASU", 
            "address": "1151 S. Forest Ave",
            "city": "Tempe", "state": "AZ", "zip": "85281", 
            "domain": "asu.edu", 
            "logo": "asu.png"
        },
        {
            "name": "University of Central Florida", 
            "short": "UCF", 
            "address": "4000 Central Florida Blvd",
            "city": "Orlando", "state": "FL", "zip": "32816", 
            "domain": "ucf.edu", 
            "logo": "ucf.png"
        },
        {
            "name": "The Ohio State University", 
            "short": "OSU", 
            "address": "281 W Lane Ave",
            "city": "Columbus", "state": "OH", "zip": "43210", 
            "domain": "osu.edu", 
            "logo": "osu.png"
        },
        {
            "name": "University of Texas at Austin", 
            "short": "UT", 
            "address": "110 Inner Campus Dr",
            "city": "Austin", "state": "TX", "zip": "78712", 
            "domain": "utexas.edu",
            "logo": "utexas.svg"
        },
        {
            "name": "Georgia Institute of Technology", 
            "short": "Georgia Tech", 
            "address": "225 North Ave NW",
            "city": "Atlanta", "state": "GA", "zip": "30332", 
            "domain": "gatech.edu",
            "logo": "gatech.png"
        }
    ]

    DEPARTMENTS = ["Computer Science", "Electrical Engineering", "Business Administration", "Psychology", "Biology", "Economics", "Mechanical Engineering", "Graphic Design"]
    POSITIONS = ["Professor", "Associate Professor", "Assistant Professor", "Lecturer", "Senior Researcher", "Department Chair"]
    
    FIRST_NAMES = ["James", "Robert", "John", "Michael", "David", "William", "Richard", "Joseph", "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George", "Timothy", "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Sandra", "Margaret", "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Dorothy", "Melissa", "Deborah"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"]

    STREETS = ["Maple Ave", "Oak St", "Washington Blvd", "Lakeview Dr", "Parkway Dr", "Main St", "Highland Ave", "Broad St", "Cherry Ln", "Sunset Dr"]

    @classmethod
    def generate_address(cls, city, state, zip_code):
        num = random.randint(100, 9999)
        street = random.choice(cls.STREETS)
        return f"{num} {street}, {city}, {state} {zip_code}"

    @classmethod
    def generate_student_id(cls):
        # Format: NNNNNN-NNNN (e.g. 656709-6626)
        part1 = "".join(random.choices(string.digits, k=6))
        part2 = "".join(random.choices(string.digits, k=4))
        return f"{part1}-{part2}"

    @classmethod
    def generate_employee_id(cls, uni_short):
        # Format: UNI-NNNNNN (e.g. GMU-305006)
        num = "".join(random.choices(string.digits, k=6))
        return f"{uni_short}-{num}"

    @classmethod
    def generate_passport(cls):
        # Alphanumeric (e.g. CM89D2QGL)
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=9))

    @classmethod
    def generate_student(cls, university_name=None):
        if university_name:
            uni = next((u for u in cls.UNIVERSITIES if u["name"] == university_name), random.choice(cls.UNIVERSITIES))
        else:
            # 默认使用 ASU 
            uni = next((u for u in cls.UNIVERSITIES if u["short"] == "ASU"), random.choice(cls.UNIVERSITIES))
            
        first_name = random.choice(cls.FIRST_NAMES)
        last_name = random.choice(cls.LAST_NAMES)
        
        now = datetime.now()
        # 针对 2025 年底，生成 2028 年左右毕业的学生
        # 有效期 2028-05-30
        grad_date = datetime(now.year + 3, 5, random.randint(15, 30))
        issue_date = grad_date - timedelta(days=365*3 + 270) # 大约 4 年学制，已过 1.5 年
        birth_date = issue_date - timedelta(days=random.randint(18, 20)*365 + random.randint(0, 365))
        
        return {
            "type": "student",
            "firstName": first_name,
            "lastName": last_name,
            "fullName": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@{uni['domain']}",
            "birthDate": birth_date.strftime("%Y-%m-%d"),
            "university": uni["name"],
            "universityShort": uni["short"],
            "universityAddress": f"{uni['city']}, {uni['state']} {uni['zip']}",
            "studentId": cls.generate_student_id(),
            "address": cls.generate_address(uni['city'], uni['state'], uni['zip']),
            "major": random.choice(cls.DEPARTMENTS),
            "term": f"Fall {now.year}",
            "issueDate": issue_date.strftime("%m/%d/%Y"),
            "validUntil": grad_date.strftime("%m/%d/%Y"),
            "passportNo": cls.generate_passport(),
            "gpa": round(random.uniform(3.2, 4.0), 2)
        }

    @classmethod
    def generate_teacher(cls):
        uni = random.choice(cls.UNIVERSITIES)
        first_name = random.choice(cls.FIRST_NAMES)
        last_name = random.choice(cls.LAST_NAMES)
        
        now = datetime.now()
        hire_year = now.year - random.randint(2, 10)
        hire_date = datetime(hire_year, random.randint(1, 12), random.randint(1, 28))
        birth_date = hire_date - timedelta(days=random.randint(28, 45)*365)
        
        return {
            "type": "teacher",
            "firstName": first_name,
            "lastName": last_name,
            "fullName": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@{uni['domain']}",
            "birthDate": birth_date.strftime("%Y-%m-%d"),
            "university": uni["name"],
            "universityShort": uni["short"],
            "universityAddress": f"{uni['city']}, {uni['state']} {uni['zip']}",
            "employeeId": cls.generate_employee_id(uni['short']),
            "address": cls.generate_address(uni['city'], uni['state'], uni['zip']),
            "department": random.choice(cls.DEPARTMENTS),
            "position": random.choice(cls.POSITIONS),
            "hireDate": hire_date.strftime("%m/%d/%Y"),
            "salary": random.randint(65000, 150000),
            "referenceNo": f"HR-{now.year}-{random.randint(1000, 9999)}"
        }

def main():
    import json
    provider = AcaGenProvider()
    
    print("--- Generated Student Profile ---")
    student = provider.generate_student()
    print(json.dumps(student, indent=2))
    
    print("\n--- Generated Teacher Profile ---")
    teacher = provider.generate_teacher()
    print(json.dumps(teacher, indent=2))

if __name__ == "__main__":
    main()
