from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def student_database():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        searchword = request.form.get("searchword", "")
        results, result_number, errors = filter_messages(username, password, searchword)
        return render_template("base.html", results=results, result_number=result_number, errors=errors)
    else:
        return render_template("base.html", results="", result_number="", errors="")


def filter_messages(username, password, searchword):
    """ returns rows from the piep entity which contain the search request
    input: -

    output: rows from the piep entity
    """
    # let op: je kunt niet zoeken op speciale tekens: %_'

    # de search request wordt aangepast zodat het werkt met de like operator
    search_on = "%" + str(searchword) + "%"
    # correct user naam wordt gevormd
    username = username + "@hannl-hlo-bioinformatica-mysqlsrv"
    try:
        # connectie wordt aangemaakt, en query uitgevoerd
        conn = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                       db="nbgcu",
                                       user=username,
                                       password=password)
        cursor = conn.cursor()
        cursor.execute("select bericht, datum, tijd, concat(voornaam, ' ', achternaam) "
                       "from student "
                       "join piep using(student_nr) "
                       "where bericht like '%s'"  
                       "order by datum desc, tijd desc" % search_on)

        return_list = []
        # counter die het aantal rijen telt
        result_number = 0
        # indxes om items in de lijst aan te passen
        indexes = [1, 2]
        for row in cursor:
            # de rijen uit de database zijn tuples. Omdat ik die rijen wil aanpassen, maak ik er eerst lijsten van
            row = list(row)
            # omdat de datum en tijd niet kunnen worden omgezet in het html bestand, doe ik dat hier.
            date = str(row[1])
            time = str(row[2])
            replace_date_time = [date, time]
            # nu moet de datum en tijd 'code' die in de originele rij staat, vervangen worden met de 'leesbare' datum
            # en tijd
            for (index, replacement) in zip(indexes, replace_date_time):
                row[index] = replacement
            return_list.append(row)
            result_number += 1

        cursor.close()
        conn.close()

        # de lijst wordt returned. In het html document staat de code voor het weergeven van de rijen
        return return_list, result_number, ""
    except mysql.connector.Error as err:
        return "", "", "Looks like something went wrong. Please login first with a valid username and password before" \
                       " firing a search request"


if __name__ == '__main__':
    app.run()
