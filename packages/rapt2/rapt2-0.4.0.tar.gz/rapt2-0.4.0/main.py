from pprint import pprint

from rapt2.rapt import Rapt


def main():
    rapt = Rapt(grammar="Extended Grammar")
    schema = {}

    # Relational algebra expressions in parser syntax
    expressions = [
        "Person_URA(ssn, empid, name, hdate, phone, email, dept, manager);",
        "Person := \\project_{ssn, name} Person_URA;",
        "PED := \\project_{ssn, empid} \\select_{defined(empid) and defined(hdate) and defined(dept) and defined(manager)} Person_URA;",
        "PED_Dept := \\project_{empid, dept} \\select_{defined(empid) and defined(hdate) and defined(dept) and defined(manager)} Person_URA;",
        "dept_manager := \\project_{dept, manager} \\select_{defined(empid) and defined(hdate) and defined(dept) and defined(manager)} Person_URA;",
        "Employee := \\project_{ssn, empid} \\select_{defined(empid) and defined(hdate)} Person_URA;",
        "Employee_Date := \\project_{empid, hdate} \\select_{defined(empid) and defined(hdate)} Person_URA;",
        "Person_Phone := \\project_{ssn, phone} Person_URA;",
        "Person_Email := \\project_{ssn, email} Person_URA;",
        "PersonURA := \\project_{ssn, empid, name, hdate, phone, email, dept, manager} (Person \\natural_join Person_Phone \\natural_join Person_Email \\natural_join Employee \\natural_join Employee_Date \\natural_join PED \\natural_join PED_Dept \\natural_join Dept_Manager);",
    ]

    

    # Convert expressions list to a single string
    single_expression = " ".join(expressions)

    for s in rapt.to_qtree(single_expression, schema):
        print(s)
    # Process the single expression
    #sql = rapt.to_sql(single_expression, schema)
    #pprint(sql[-1])


if __name__ == "__main__":
    main()
