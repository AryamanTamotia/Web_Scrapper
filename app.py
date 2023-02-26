from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import csv
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            filename = searchString + ".csv"
            fw = open(filename, "w")
            fw_writer=csv.writer(fw)
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            client = pymongo.MongoClient("mongodb+srv://atamotia:atamotia@cluster0.av6ep6v.mongodb.net/?retryWrites=true&w=majority")
            db = client['Web_Scrapper']
            db_coll = db[searchString]
            for box in bigboxes:
                try: 
                    productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                    prodRes = requests.get(productLink)
                    prodRes.encoding='utf-8'
                    prod_html = bs(prodRes.text, "html.parser")
                    try:
                            prodName = prod_html.find_all('span', {'class': 'B_NuCI'})[0].text
                    except:
                            prodName = 'No Name'
                            logging.info("name")
    
                    commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
                
                    for commentbox in commentboxes:

                        try:
                            name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                        except:
                            name = 'No Name'
                            logging.info("name")

                        try:
                            rating = commentbox.div.div.div.div.text


                        except:
                            rating = 'No Rating'
                            logging.info("rating")

                        try:
                            commentHead = commentbox.div.div.div.p.text

                        except:
                            commentHead = 'No Comment Heading'
                            logging.info(commentHead)
                        try:
                            comtag = commentbox.div.div.find_all('div', {'class': ''})
                            custComment = comtag[0].div.text
                        except Exception as e:
                            comtag = 'No Comment'
                            logging.info(e)

                        fw_writer.writerow([prodName,name,rating,commentHead,custComment])
                        mydict = {"Product": prodName, "Name": name, "Rating": rating, "CommentHead": commentHead,
                                "Comment": custComment}
                        reviews.append(mydict)
                except:
                    continue
                
            db_coll.insert_many(reviews)
            logging.info("log my final result {}".format(reviews))
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
