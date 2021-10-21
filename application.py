from cs50 import SQL
from flask import Flask, redirect, render_template ,jsonify, session, request
from flask_session import Session
from helpers import login_required , apology
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError 
from tempfile import mkdtemp 
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)


 

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///myitems.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        sort=request.form.get("sortby")
        typ=request.form.get("order")
        if not sort:
            return render_template("index.html", items=db.execute("SELECT * FROM items ORDER BY count DESC ")) 
        if sort == "name":
            if typ=="descending":
                return render_template("index.html", items=db.execute("SELECT * FROM items ORDER BY item DESC  "))
            return render_template("index.html", items=db.execute("SELECT * FROM items ORDER BY item ASC  "))
        
        elif typ=="descending": 
            return render_template("index.html", items=db.execute("SELECT * FROM items ORDER BY count DESC "))
        return render_template("index.html", items=db.execute("SELECT * FROM items ORDER BY count ASC  "))    
     
    return render_template( "/index.html" ,items=db.execute("SELECT * FROM items ORDER BY count DESC "))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Buy shares of stock"""
    if request.method == "POST":
        db.execute("BEGIN TRANSACTION")
        if not request.form.get("name"):
            return apology("must provide name ")
        elif not request.form.get("count"):
            return apology("must provide the number")
        name=request.form.get("name")
        count=request.form.get("count")
        if not count.isnumeric():
            return apology("enter valid number for the pieces") 
        db.execute("INSERT INTO items (item , count) VALUES(?,?)",name, count) 
        db.execute("COMMIT")  
        return redirect("/")  
      
    return render_template("add.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        item=request.form.get("item")
        if not item:
            return apology("enter valid input") 
        oldc=db.execute("SELECT count FROM items WHERE item = ? ", item)[0]["count"]  
        sell= request.form.get("count")
        if not sell:
            return apology("enter valid input")
        if not sell.isnumeric():
            return apology("enter valid number for the pieces") 
        count= oldc - sell       
        if count<0:
            return apology("There is no enogh items ")
            
        db.execute("UPDATE items SET count = ? WHERE item  = ? ",count, item )
        return redirect("/")  
    
    return render_template("/sell.html") 


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")
 
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("/login.html") 


@app.route("/register", methods=["GET", "POST"])
def register():
    return apology("this feature is not available yet to log in use username: m  password: 1") 
    if request.method == "POST":  
        username=request.form.get("username")
        password=request.form.get("password")
        cpassword=request.form.get("cpassword")
        if not username:
            return apology("most provide username")
        if not password:
            return apology("most provide password")
        if not cpassword:
            return apology("most confirm password")
        if password != cpassword :
            return apology("most confirm password") 
        db.execute("INSERT INTO users(username ,hash) VALUES (?,?)",username , generate_password_hash(password))
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"] 
        return  redirect("/")  
    return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("This feature does not work yet ")


@app.route("/delete") 
@login_required
def delete(): 

    return apology("this feature does not work yet ")


@app.route("/update", methods=["GET", "POST"]) 
@login_required
def update():

    return apology("This feature does not work yet ")


@app.route("/search")
@login_required
def search():
    """Sell shares of stock"""
    items = db.execute("SELECT * FROM items WHERE item LIKE ? ", "%" + request.args.get("q") + "%") 
    return jsonify(items) 


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name) 
# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)  