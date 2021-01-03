from django.shortcuts import render, redirect
from django.http import HttpResponse
import logging
import requests
import time


def check_float(numb):
    try:
        float(numb)
        return True
    except ValueError:
        return False


# Create your views here.

def home(request):
    mods = []
    res = ""
    num = 20  # max num of components
    for i in range(num):
        mods.append(i + 1)
    if "submit" in request.GET:
        # WRITE BACK END CODE HERE, PLACING FINAL RESULT IN res VARIABLE:

        grades = []
        weights = []
        scales = []
        mustpasses = []

        for j in range(1, int(request.GET['numComp']) + 1):
            exec("grades.append(request.GET['grade" + str(j) + "'])")
            exec("weights.append(request.GET['weight" + str(j) + "'])")
            exec("scales.append(request.GET.get('scale" + str(j) + "','0'))")
            exec("mustpasses.append(request.GET.get('mustpass" + str(j) + "', 'N'))")

        print('pass', mustpasses)
        print('weight', weights)
        print('grades', grades)
        res = average_mod(weights, grades, scales, mustpasses)

    if res != "":
        resultAchieved = 1
    else:
        resultAchieved = 0

    return render(request, 'home.html', {'number': num, 'list': mods, 'result': res, 'calcFlag': resultAchieved})


def average_mod(weight, score, grad_mode, mustpass):
    Standart = {90: "A+", 80: "A", 70: "A-", 66.67: "B+", 63.33: "B", 60: "B-", 56.67: "C+", 53.33: "C", 50: "C-",
                46.67: "D+", 43.33: "D", 40: "D-", 0: 0}
    Alt_Lin = {95: "A+", 90: "A", 85: "A-", 80: "B+", 75: "B", 70: "B-", 65: "C+", 60: "C", 55: "C-", 50: "D+", 45: "D",
               40: "D-", 0: 0}
    Alt_Non_Lin = {90: "A+", 80: "A", 70: "A-", 67.78: "B+", 65.56: "B", 63.33: "B-", 61.12: "C+", 58.89: "C",
                   56.67: "C-", 54.43: "D+", 52.22: "D", 50: "D-", 0: 0}
    China = {96.67: "A+", 93.33: "A", 90: "A-", 86.67: "B+", 83.34: "B", 80: "B-", 76.67: "C+", 73.33: "C", 70: "C-",
             66.67: "D+", 63.33: "D", 60: "D-", 0: 0}
    Calc_point = {"A+": 20.5, "A": 19.5, "A-": 18.5, "B+": 17.5, "B": 16.5, "B-": 15.5, "C+": 14.5, "C": 13.5,
                  "C-": 12.5, "D+": 11.5, "D": 10.5, "D-": 9.5, 0: 0}
    Lower = {20: "A+", 19: "A", 18: "A-", 17: "B+", 16: "B", 15: "B-", 14: "C+", 13: "C", 12: "C-", 11: "D+", 10: "D",
             9: "D-"}

    mod_tot = 0
    score2 = []
    ErrStr = []
    w_sum = 0

    for i in weight:
        if check_float(i) == False or (float(i) > 100 and float(i) < 0):
            return ("Error, a Weight Value is Invalid, Negative, or Exceeds 100: " + str(i) + "; ")
        w_sum += float(i)
    if (w_sum != 100):
        return ("Error: The Sum of all Component Weights Should be 100, but is currently " + str(w_sum) + "; ")

    for i in score:
        if i in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "E+", "E", "E-", "F+", "F", "F-",
                 "G+", "G", "G-", "NM"]:
            i = i
        elif check_float(i) and (float(i) <= 100 and float(i) >= 0):
            i = i
        else:
            return ("Error, grade is invalid, either negative or exceeds 100: " + str(i)+ "; ")

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
        else:
            return("Please Specify Grading Scales" + "; ")

        # converting grades ABC or Numb to Numb
        if score[i] in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-"]:
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
            mod_tot += Calc_point[score2[i]] * float(weight[i]) / 100.0
        except ValueError:
            mod_tot = mod_tot

    # yes or no
    for i in range(len(score2)):
        if score2[i] == 0 and mustpass[i] == "Y":
            return "Fail;0"
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
               "Alternative linear conversion grade scale 60%": 4}
    module = (request.GET['modCode'])
    module = list(module)
    for i in range(len(module)):
        module[i] = module[i].capitalize()
    module = "".join(module)
    mods = []
    for i in range(20):
        mods.append(i + 1)

    url = 'https://sisweb.ucd.ie/usis/!W_HU_MENU.P_PUBLISH?p_tag=MODULE&MODULE=' + module
    r = requests.get(url)
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
        grading.append(gr_dict[i[4][:(i[4].index("</TD>"))]])
        if (grading[-1] == 0):
            ErrStr.append("graded")
            ErrCodes.append(str(len(grading)))

        weight.append((i[6][(i[6].index("\"rightaligntext\">") + len("\"rightaligntext\">")):(i[6].index("</TD>"))]))
        mustpass.append(i[5][:(i[5].index("</TD>"))])

    for i in comp:
        i = i.split(" ")
        for j in i:
            try:
                j = j[0].capitalize() + j[1:]
            except IndexError:
                j = j[0].capitalize()
        i = (elem[0:4] for elem in i)
        i = " ".join(i)


    return render(request, 'home.html',
                  {'returnedN': len(comp), 'names': comp, 's': grading, 'w': weight, 'm': mustpass, 'number': 20,
                   'list': mods, 'error': ErrStr, 'calcFlag': 0, 'title': name, 'codes': ErrCodes})