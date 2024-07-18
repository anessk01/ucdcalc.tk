from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import time
from .models import Counter

#import random
#import ssl
#from requests_html import HTMLSession

#from bs4 import BeautifulSoup

#import re


def check_float(numb):
    try:
        float(numb)
        return True
    except ValueError:
        return False

# t
def home(request):
    use_count = increment_use_count()
    mods = []
    res = ""
    num = 20  # max num of components
    for i in range(num):
        mods.append(i + 1)
    if "submit" in request.GET:

        grades = []
        weights = []
        scales = []
        mustpasses = []

        for j in range(1, int(request.GET['numComp']) + 1):
            exec("grades.append(request.GET['grade" + str(j) + "'])")
            exec("weights.append(request.GET['weight" + str(j) + "'])")
            exec("scales.append(request.GET.get('scale" + str(j) + "','0'))")
            exec("mustpasses.append(request.GET.get('mustpass" + str(j) + "', 'N'))")

        res = average_mod(weights, grades, scales, mustpasses)

    if res != "":
        resultAchieved = 1
    else:
        resultAchieved = 0

    return render(request, 'home.html', {'number': num, 'list': mods, 'result': res, 'calcFlag': resultAchieved, 'use_count': use_count})




def average_mod(weight, score, grad_mode, mustpass):
    Standart = {90: "A+", 80: "A", 70: "A-", 66.67: "B+", 63.33: "B", 60: "B-", 56.67: "C+", 53.33: "C", 50: "C-",
                46.67: "D+", 43.33: "D", 40: "D-", 36.67 : "E+", 33.33 : "E", 30:"E-", 26.67:"F+", 23.33:"F", 20.0:"F-", 16.67:"G+", 13.33:"G", 0.01:"G-", 0: 0}
    Alt_Lin = {95: "A+", 90: "A", 85: "A-", 80: "B+", 75: "B", 70: "B-", 65: "C+", 60: "C", 55: "C-", 50: "D+", 45: "D", 40: "D-", 35 : "E+", 30 : "E", 25:"E-", 20:"F+", 15:"F", 10:"F-", 5:"G+", 0.02:"G", 0.01:"G-", 0: 0}
    Alt_Non_Lin = {90: "A+", 80: "A", 70: "A-", 67.78: "B+", 65.56: "B", 63.33: "B-", 61.12: "C+", 58.89: "C", 56.67: "C-", 54.43: "D+", 52.22: "D", 50: "D-", 45: "E+", 40: "E", 35: "E-", 30: "F+",25: "F", 20: "F-", 15: "G+", 10: "G", 0.01: "G-", 0: 0}
    China = {96.67: "A+", 93.33: "A", 90: "A-", 86.67: "B+", 83.34: "B", 80: "B-", 76.67: "C+", 73.33: "C", 70: "C-",
             66.67: "D+", 63.33: "D", 60: "D-", 0: 0}
    Calc_point = {"A+": 20.5, "A": 19.5, "A-": 18.5, "B+": 17.5, "B": 16.5, "B-": 15.5, "C+": 14.5, "C": 13.5, "C-": 12.5, "D+": 11.5, "D": 10.5, "D-": 9.5,  "E+":8.5,  "E":7.5, "E-":6.5,  "F+":5.5, "F":4.5, "F-": 3.5,  "G+":2.5,  "G":1.5,  "G-":0.5, 0: 0, "P": 20.5}
    Lower = {20: "A+", 19: "A", 18: "A-", 17: "B+", 16: "B", 15: "B-", 14: "C+", 13: "C", 12: "C-", 11: "D+", 10: "D",
             9: "D-"}
    Pass_list = {"PASS": "P", "pass": "P", "Pass": "P", "P": "P", "FAIL": "F", "fail": "F", "Fail": "F", "F": "F"}

    mod_tot = 0
    score2 = []
    ErrStr = []
    w_sum = 0

    # input validation
    for i in weight:
        if check_float(i) == False or (float(i) > 100 or float(i) < 0):
            return ("Error, a Weight Value is Invalid, Negative, or Exceeds 100: " + str(i) + "; ")
        w_sum += float(i)
    if (w_sum != 100):
        return ("Error: The Sum of all Component Weights Should be 100, but is currently " + str(w_sum) + "; ")

    for i in range(len(score)):
        if score[i] in Pass_list:
            score[i] = Pass_list[score[i]]

    for i in range(len(score)):
        if grad_mode[i] == "5" and score[i] in ["P", "F"]:
            i = i
        elif grad_mode[i]=="5":
            return("Please Ensure Inputs for pass/fail components are either (pass) or (fail) ; ")
        elif score[i] in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "E+", "E", "E-", "F+",
                          "F", "F-", "G+", "G", "G-", "NM"]:
            i = i
        elif check_float(score[i]) and (float(score[i]) <= 100 and float(score[i]) >= 0):
            if (grad_mode[i] == "0"):
                return ("Error, please enter the grade in alphabetical form, if you select (Graded) scheme ; ")
            else:
                i = i
        else:
            return ("Error, grade is invalid, either negative or exceeds 100: " + str(score[i]) + "; ")

    for i in range(len(score)):
        # grading mode def
        mode = grad_mode[i]

        if mode == "1":
            mode = Standart
        elif mode == "2":
            mode = Alt_Lin
        elif mode == "3":
            mode = Alt_Non_Lin
        elif mode == "4":
            mode = China

        # converting grades ABC or Numb to Numb
        if score[i] in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "E+", "E", "E-", "F+", "F", "F-", "G+", "G", "G-", "P"]:
            score2.append(score[i])
        elif check_float(score[i]):
            for j in mode:
                if float(score[i]) >= j:
                    score2.append(mode[j])
                    break
        else:
            score2.append(0)

        # finding tot grade in 21 scale
        try:
            print("i", i, Calc_point[score2[i]])
            mod_tot += Calc_point[score2[i]] * float(weight[i]) / 100.0
            

        except ValueError:
            mod_tot = mod_tot

    print("MOd_tot", mod_tot)
    # yes or no in must pass
    for i in range(len(score2)):
                    
        if (score2[i] == 0 or score2[i] in ["E+","E", "E-","F+","F","F-","G+","G","G-"]) and mustpass[i] == "Y":
            return "Fail;0"

    loc = 0
    for i in grad_mode:
        print(i)
        if (i == "5"):
            loc += 1
    print(loc)
    if (loc == len(grad_mode) and mod_tot >= 9):
        return "PASS;4.2"

    # returning the overall grade, mark and all the other data
    for i in Lower:
        if mod_tot >= i:
            print(type(Lower[i]), type(str((i + 1) / 5)))

            return str(Lower[i]) + ";" + str((i + 1) / 5)
    return "Fail;0"


def scrapeUCD(request):
    ErrStr = []
    ErrCodes = []
    comp = []
    grading = []
    weight = []
    mustpass = []

    gr_dict = {"Graded": 0, "Standard conversion grade scale 40%": 1,
               "Alternative linear conversion grade scale 40%": 2,
               "Alternative non-linear conversion grade scale 50%": 3,
               "Alternative linear conversion grade scale 60%": 4,
               "Pass/Fail Grade Scale": 5}
    module = (request.GET['modCode'])
    module = list(module)
    for i in range(len(module)):
        module[i] = module[i].capitalize()
    module = "".join(module)
    mods = []
    for i in range(20):
        mods.append(i + 1)
    
    url = 'https://sisweb.ucd.ie/usis/!W_HU_MENU.P_PUBLISH?p_tag=MODULE&MODULE=' + module
    proxies = {
        "http":None,
        "https":None
    }
    r = requests.get(url, verify = False, proxies = proxies)
    str_of_url = str(r.content, 'utf-8')

    try:
        ind = str_of_url.index("Assessment Strategy")
    except ValueError:
        ErrStr.append("codeNotFound")
        ErrCodes.append(" ")
        return render(request, 'home.html',
                      {'returnedN': len(comp), 'names': comp, 's': grading, 'w': weight, 'm': mustpass, 'number': 20,
                       'list': mods, 'error': ErrStr, 'codes': ErrCodes, 'calcFlag': 0})

    nameInd = str_of_url.index("pageTitle")
    name = str_of_url[nameInd:]
    name = name[name.index(">") + 1: name.index("<")]
    print(name)

    str1 = str_of_url[ind:]
    ind1 = str1.index("</tr></THEAD><TBODY")
    ind2 = str1.index("</TBODY><TFOOT>")
    str1 = str1[ind1:ind2]
    str1 = str1.split("tr ID=CB100-30|")[1:]

    for i in str1:
        i = i.split("<TD>")
        comp.append(i[1][:(i[1].index("</TD>"))])
        try:
            grading.append(gr_dict[i[4][:(i[4].index("</TD>"))]])
        except KeyError:
             grading.append(gr_dict["Graded"])
        if (grading[-1] == 0):
            ErrStr.append("graded")
            ErrCodes.append(str(len(grading)))

        weight.append((i[6][(i[6].index("\"rightaligntext\">") + len("\"rightaligntext\">")):(i[6].index("</TD>"))]))
        mustpass.append(i[5][:(i[5].index("</TD>"))])

    for i in range(len(comp)):
        comp[i] = (comp[i].split(" "))[:5]
        for j in range(len(comp[i])):
            print(comp[i][j])
            try:
                comp[i][j] = comp[i][j][0].capitalize() + comp[i][j][1:]
            except IndexError:
                try:
                    comp[i][j] = comp[i][j][0].capitalize()
                except IndexError:
                    j = j
        comp[i] = " ".join(comp[i])

    return render(request, 'home.html',
                  {'returnedN': len(comp), 'names': comp, 's': grading, 'w': weight, 'm': mustpass, 'number': 20,
                   'list': mods, 'error': ErrStr, 'calcFlag': 0, 'title': name, 'codes': ErrCodes})


#print(average_mod([50, 50], ["B", "F-"], ["0", "0"], ["N", "Y"]))

def increment_use_count():
    val = Counter.get_counter_value()
    counter = Counter.objects.get(pk=1)
    counter.increment()
    return val

def overall(request):
    print("-->", request.GET)
    use_count = increment_use_count()
    try:
        if(request.GET['modGrade1'] is not None):
            list=[]
            creditlist = []
            failFlag = False
            try:
                for j in range(1, int(request.GET['numCompOVR']) + 1):
                    try:
                        exec("list.append(request.GET['modGrade" + str(j) + "'])")
                        exec("creditlist.append(request.GET['modCredits" + str(j) + "'])")
                    except:
                        failFlag = True
                        break
            except:
                failFlag = True
            if(not failFlag):
                calc_flag = 1
                try:
                    print(creditlist)
                    result = for_retards(list, creditlist)
                except:
                    result = "Error. Check all inputs and resubmit"
                    failFlag = True
            else:
                result = "Error. Check all inputs and resubmit"
                failFlag = True
                calc_flag = 1        
    except:
        result = None
        failFlag = True
        calc_flag = 0
    if request.headers.get('HX-Request'):
        try:
            if result >= 3.68:
                hons = "(1:1)"
            elif result >= 3.08:
                hons = "(2:1)"
            elif result >= 2.48:
                hons = "(2:2)"
            else:
                hons = ""
        except:
            hons = ""
            
        return render(request, 'overall_result.html', {'result': result, 'award': hons, 'failFlag': failFlag})
    else:
        return render(request, "overall.html", {'calcFlag': 0, 'number': 13,'list': range(1, 13), 'use_count': use_count})


def for_retards(list_grades, list_credits):
    gp = {"A+":4.2, "A":4, "A-":3.8, "B+":3.6, "B":3.4, "B-":3.2, "C+":3, "C":2.8, "C-":2.6, "D+":2.4, "D":2.2, "D-":2, "E": 1.6, "F": 1.0, "G": 0.4, "NM":0, "NG":0, "ABS":0}
    sum = 0
    sum_credits = 0
    # length = 0
    counter = 0
    for grade in list_grades:
        if grade.lower() not in ["p", "ds", "pass"]:
            # try:
            if(float(list_credits[counter]) <=0):
                raise TypeError
            sum += gp[grade]*float(list_credits[counter])
            sum_credits += float(list_credits[counter])
            # length +=1
            # except:
            #     #here we might want to throw an error instead of just returning the avg as is idk
            #     return "Error. Check all inputs and resubmit"
            # average += 0
        counter+=1
            
    return round(sum/sum_credits, 3)


# def get_counter(request):
#     value = Counter.get_counter_value()
#     return render(request, 'use_count.html', {'counter_value': value})

#print(for_retards(["A+", "A", "A-", "ABS"]))
